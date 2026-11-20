"""CONSUMER S8/S10 persistente: Kafka -> Spark Structured Streaming -> PostgreSQL.
Ejecutar con spark-submit mediante el perfil de Docker Compose `streaming`.
Kafka Source: dos tópicos; watermark 2h; deduplicación; ventanas 1h;
modelos 1/2/3h entrenados en el notebook; checkpoint independiente por consulta.
"""
from __future__ import annotations
import logging
import math
import os
import threading
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import psycopg2
from psycopg2.extras import execute_values
from pyspark.ml import PipelineModel
from pyspark.sql import SparkSession, functions as F, types as T

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# --- Hora de Perú (UTC-5, sin horario de verano) ---------------------------------------------
# PySpark entrega los timestamps a Python como datetime SIN zona horaria, expresados en la hora
# local del proceso (TZ del contenedor). astimezone() sobre un datetime sin zona usa esa MISMA
# hora local, así que la conversión es exacta sea cual sea el TZ. Todo se guarda con zona -05:00.
PERU = timezone(timedelta(hours=-5), "PET")
logging.getLogger("py4j").setLevel(logging.WARNING)  # oculta "Received command c on object id ..."


def hora_peru(dt):
    """Convierte un timestamp de PySpark (o un texto ISO) en datetime con zona de Perú."""
    if dt is None:
        return None
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(PERU)

ROOT = Path(os.getenv("AGRO_ROOT", "/home/jovyan/work/Sensorhumedad"))
KAFKA = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")
SCHEMA_FILE = Path("/opt/agrosmart-sql/schema.sql")
TOPICO_SENSOR = "agrosmart-u2-humedad-telemetria"
TOPICO_EMPRESA = "agrosmart-u2-humedad-empresarial"
CP = ROOT / "checkpoints"
CP.mkdir(parents=True, exist_ok=True)

def conexion():
    return psycopg2.connect(host=os.getenv("POSTGRES_HOST","postgres"),
      dbname=os.getenv("POSTGRES_DB","agrosmart_u2"),
      user=os.getenv("POSTGRES_USER","agrosmart"),
      password=os.environ["POSTGRES_PASSWORD"],connect_timeout=10,
      options="-c TimeZone=America/Lima")


def preparar_db():
    with conexion() as conn, conn.cursor() as cur:
        cur.execute(SCHEMA_FILE.read_text(encoding="utf-8"))
    logging.info("Esquema PostgreSQL preparado")


def guardar_lote(sql, filas, cur, chunk=250):
    if not filas:
        return
    for offset in range(0, len(filas), chunk):
        execute_values(cur, sql, filas[offset:offset+chunk], page_size=chunk)


def monitor_metricas(queries, stop):
    """Observa progreso por consulta; heartbeat no inventa progreso sin eventos."""
    while not stop.is_set():
        try:
            with conexion() as conn, conn.cursor() as cur:
                for nombre, consulta in list(queries.items()):
                    p = consulta.lastProgress or {}
                    duracion = (p.get("durationMs") or {}).get("triggerExecution")
                    retrasos = []
                    for fuente in p.get("sources", []):
                        value = (fuente.get("metrics") or {}).get("maxOffsetsBehindLatest")
                        if value is not None:
                            try: retrasos.append(float(value))
                            except (TypeError, ValueError): pass
                    # NULL significa no medido, no cero.
                    lag = max(retrasos) if retrasos else None
                    exc = consulta.exception()
                    cur.execute("""
                     INSERT INTO metricas_pipeline
                       (consulta,activa,batch_id,filas_entrada,duracion_ms,
                        retraso_offsets,fecha_progreso_utc,observado_utc,error)
                     VALUES (%s,%s,%s,%s,%s,%s,%s,NOW(),%s)
                     ON CONFLICT(consulta) DO UPDATE SET
                       activa=EXCLUDED.activa,batch_id=EXCLUDED.batch_id,
                       filas_entrada=EXCLUDED.filas_entrada,duracion_ms=EXCLUDED.duracion_ms,
                       retraso_offsets=EXCLUDED.retraso_offsets,
                       fecha_progreso_utc=EXCLUDED.fecha_progreso_utc,
                       observado_utc=NOW(),error=EXCLUDED.error
                    """, (nombre, consulta.isActive, p.get("batchId"),
                          p.get("numInputRows"),duracion,lag,p.get("timestamp"),
                          str(exc) if exc else None))
        except Exception as exc:
            logging.warning("No pudo guardar métricas: %s", exc)
        stop.wait(10)


def main():
    preparar_db()
    modelos = {}
    for h in (1,2,3):
        ruta = ROOT / "modelos" / f"humedad_{h}h"
        if not ruta.exists():
            raise FileNotFoundError(f"Entrena primero en Jupyter: falta {ruta}")
    spark = (SparkSession.builder.master("local[2]")
        .appName("AgroSmart-U2-Consumer-Spark")
        .config("spark.sql.shuffle.partitions","2")
        .config("spark.sql.session.timeZone","UTC")
        .getOrCreate())
    spark.sparkContext.setLogLevel("WARN")
    for h in (1,2,3):
        modelos[h] = PipelineModel.load(str(ROOT / "modelos" / f"humedad_{h}h"))

    sensor_schema = T.StructType([
      T.StructField("evento_id",T.StringType()),
      T.StructField("fecha_evento",T.StringType()),
      T.StructField("emitido_utc",T.StringType()),
      T.StructField("ubicacion",T.StringType()),
      T.StructField("humedad_suelo_m3m3",T.DoubleType()),
      T.StructField("humedad_suelo_pct",T.DoubleType()),
      T.StructField("humedad_aire_pct",T.DoubleType()),
      T.StructField("origen",T.StringType()),
      T.StructField("modo_publicacion",T.StringType())
    ])
    emp_schema = T.StructType([
      T.StructField("evento_id",T.StringType()),
      T.StructField("evento_telemetria_id",T.StringType()),
      T.StructField("fecha_evento",T.StringType()),
      T.StructField("ubicacion",T.StringType()),
      T.StructField("tipo",T.StringType()),
      T.StructField("estado",T.StringType()),
      T.StructField("humedad_suelo_pct",T.DoubleType()),
      T.StructField("humedad_aire_pct",T.DoubleType()),
      T.StructField("umbral_demo_pct",T.DoubleType()),
      T.StructField("origen",T.StringType())
    ])
    def leer(topic, schema):
        return (spark.readStream.format("kafka")
            .option("kafka.bootstrap.servers", KAFKA)
            .option("subscribe", topic)
            .option("startingOffsets", "earliest")
            .option("failOnDataLoss", "true")
            .load().select("partition","offset",
                    F.from_json(F.col("value").cast("string"),schema).alias("dato"))
            .select("partition","offset","dato.*")
            .withColumn("fecha_evento",F.to_timestamp("fecha_evento")))

    sensor = leer(TOPICO_SENSOR,sensor_schema).filter(
        F.col("evento_id").isNotNull() & F.col("fecha_evento").isNotNull()
        & F.col("emitido_utc").isNotNull() & F.col("ubicacion").isNotNull()
        & F.col("humedad_suelo_m3m3").between(0.0,1.0)
        & F.col("humedad_suelo_pct").between(0.0,100.0)
        & F.col("humedad_aire_pct").between(0.0,100.0)
    )
    negocio = leer(TOPICO_EMPRESA,emp_schema).filter(
        F.col("evento_id").isNotNull() & F.col("evento_telemetria_id").isNotNull()
        & F.col("fecha_evento").isNotNull()
        & F.col("humedad_suelo_pct").between(0.0,100.0)
        & F.col("humedad_aire_pct").between(0.0,100.0)
    )
    s_unico = (sensor.withWatermark("fecha_evento","2 hours")
                .dropDuplicatesWithinWatermark(["evento_id"]))
    e_unico = (negocio.withWatermark("fecha_evento","2 hours")
                .dropDuplicatesWithinWatermark(["evento_id"]))
    # Una consulta stateful independiente para ventanas: evita encadenar dos
    # operadores stateful incompatibles en una misma consulta.
    ventanas = (sensor.withWatermark("fecha_evento","2 hours")
      .groupBy(F.window("fecha_evento","1 hour"),"ubicacion")
      .agg(F.count("*").alias("lecturas"),
           F.avg("humedad_suelo_pct").alias("humedad_suelo_media_pct"),
           F.avg("humedad_aire_pct").alias("humedad_aire_media_pct")))

    def lote_sensor(df, batch_id):
        start = time.monotonic()
        df.persist()
        try:
            sensor_rows = []
            for r in df.toLocalIterator():
                sensor_rows.append((r.evento_id,hora_peru(r.fecha_evento),hora_peru(r.emitido_utc),r.ubicacion,
                   r.humedad_suelo_m3m3,r.humedad_suelo_pct,r.humedad_aire_pct,
                   r.origen,r.modo_publicacion,r.partition,r.offset))
            pred_rows = []
            if sensor_rows:
                features = (df.withColumn("hora_seno", F.sin(F.hour("fecha_evento") * F.lit(2*math.pi/24)))
                    .withColumn("hora_coseno", F.cos(F.hour("fecha_evento") * F.lit(2*math.pi/24))))
                for h, modelo in modelos.items():
                    for r in modelo.transform(features).select("evento_id","fecha_evento","prediction").toLocalIterator():
                        evento = hora_peru(r.fecha_evento)
                        objetivo = evento+timedelta(hours=h)
                        pred_rows.append((r.evento_id,h,evento,objetivo,
                           float(r.prediction),modelo.stages[-1].__class__.__name__,
                           datetime.now(timezone.utc)>=objetivo))
            with conexion() as conn, conn.cursor() as cur:
                guardar_lote("""INSERT INTO eventos_telemetria
                  (evento_id,fecha_evento,emitido_utc,ubicacion,humedad_suelo_m3m3,
                   humedad_suelo_pct,humedad_aire_pct,origen,modo_publicacion,kafka_particion,kafka_offset)
                  VALUES %s ON CONFLICT(evento_id) DO NOTHING""", sensor_rows,cur)
                guardar_lote("""INSERT INTO predicciones_humedad
                  (evento_id,horizonte_h,fecha_evento,fecha_objetivo,prediccion_pct,modelo,es_retro)
                  VALUES %s ON CONFLICT(evento_id,horizonte_h) DO NOTHING""",pred_rows,cur)
            logging.info("S8/S10 telemetria batch=%s filas=%s predicciones=%s duracion_s=%.2f",
                         batch_id,len(sensor_rows),len(pred_rows),time.monotonic()-start)
        finally:
            df.unpersist()

    def lote_negocio(df,batch_id):
        filas = [(r.evento_id,r.evento_telemetria_id,hora_peru(r.fecha_evento),r.ubicacion,
                  r.tipo,r.estado,r.humedad_suelo_pct,r.humedad_aire_pct,
                  r.umbral_demo_pct,r.origen) for r in df.toLocalIterator()]
        with conexion() as conn, conn.cursor() as cur:
            guardar_lote("""INSERT INTO eventos_empresariales
              (evento_id,evento_telemetria_id,fecha_evento,ubicacion,tipo,estado,
               humedad_suelo_pct,humedad_aire_pct,umbral_demo_pct,origen)
              VALUES %s ON CONFLICT(evento_id) DO NOTHING""",filas,cur)
        logging.info("S6 negocio batch=%s filas=%s",batch_id,len(filas))

    def lote_ventanas(df,batch_id):
        filas = [(hora_peru(r.inicio),hora_peru(r.fin),r.ubicacion,r.lecturas,
                   r.humedad_suelo_media_pct,r.humedad_aire_media_pct)
                  for r in df.select(F.col("window.start").alias("inicio"),
                    F.col("window.end").alias("fin"),"ubicacion", "lecturas",
                    "humedad_suelo_media_pct","humedad_aire_media_pct").toLocalIterator()]
        with conexion() as conn,conn.cursor() as cur:
            guardar_lote("""INSERT INTO ventanas_humedad
                (inicio,fin,ubicacion,lecturas,humedad_suelo_media_pct,humedad_aire_media_pct)
                VALUES %s ON CONFLICT(inicio,fin,ubicacion) DO UPDATE SET
                lecturas=EXCLUDED.lecturas,
                humedad_suelo_media_pct=EXCLUDED.humedad_suelo_media_pct,
                humedad_aire_media_pct=EXCLUDED.humedad_aire_media_pct""",filas,cur)
        logging.info("S8 ventanas batch=%s filas=%s",batch_id,len(filas))

    consultas = {}
    for nombre,df,fn,modo in [
        ("telemetria",s_unico,lote_sensor,"append"),
        ("empresarial",e_unico,lote_negocio,"append"),
        ("ventanas",ventanas,lote_ventanas,"update")]:
        q=(df.writeStream.queryName("agrosmart_"+nombre)
            .outputMode(modo).foreachBatch(fn)
            .option("checkpointLocation",str(CP / nombre))
            .trigger(processingTime="5 seconds").start())
        consultas[nombre]=q
        logging.info("Consulta %s iniciada, id=%s", nombre,q.id)

    detener = threading.Event()
    hilo = threading.Thread(target=monitor_metricas,args=(consultas,detener),daemon=True)
    hilo.start()
    try:
        while True:
            inactivas = [(n,str(q.exception())) for n,q in consultas.items() if not q.isActive]
            if inactivas:
                raise RuntimeError(f"Consultas detenidas: {inactivas}")
            time.sleep(5)
    finally:
        detener.set()
        hilo.join(timeout=20)
        for q in consultas.values():
            if q.isActive: q.stop()
        spark.stop()


if __name__ == "__main__":
    main()
