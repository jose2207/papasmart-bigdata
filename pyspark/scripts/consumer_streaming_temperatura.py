"""CONSUMER S8/S10 persistente de la DIMENSIÓN DE MIJAEL (temperatura, Azángaro):
Kafka -> Spark Structured Streaming -> PostgreSQL. Tres consultas independientes (checkpoint propio):
  temp_telemetria : guarda eventos + inferencia de temperatura a +1 h (modelo MLlib entrenado en el cuaderno)
  temp_empresarial: guarda evaluaciones simuladas de riesgo de helada
  temp_ventanas   : ventanas de 1 h (media/mín/máx) con watermark de 2 h
"""
from __future__ import annotations
import logging, math, os, threading, time
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

ROOT = Path(os.getenv("AGRO_ROOT", "/home/jovyan/work/Sensortemperatura"))
KAFKA = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")
SQL_DIR = Path("/opt/agrosmart-sql")
TOPICO_SENSOR = "agrosmart-u2-temperatura-telemetria"
TOPICO_EMPRESA = "agrosmart-u2-temperatura-empresarial"
HORIZONTES = (1,)
CP = ROOT / "checkpoints"
CP.mkdir(parents=True, exist_ok=True)


def conexion():
    return psycopg2.connect(host=os.getenv("POSTGRES_HOST", "postgres"), dbname=os.getenv("POSTGRES_DB", "agrosmart_u2"),
                            user=os.getenv("POSTGRES_USER", "agrosmart"), password=os.environ["POSTGRES_PASSWORD"], connect_timeout=10,
                            options="-c TimeZone=America/Lima")


def preparar_db():
    with conexion() as conn, conn.cursor() as cur:
        for f in ("schema.sql", "schema_temperatura.sql"):
            cur.execute((SQL_DIR / f).read_text(encoding="utf-8"))
    logging.info("Esquema PostgreSQL preparado (base + temperatura)")


def guardar_lote(sql, filas, cur, chunk=250):
    for off in range(0, len(filas), chunk):
        execute_values(cur, sql, filas[off:off + chunk], page_size=chunk)


def monitor_metricas(queries, stop):
    while not stop.is_set():
        try:
            with conexion() as conn, conn.cursor() as cur:
                for nombre, q in list(queries.items()):
                    p = q.lastProgress or {}
                    dur = (p.get("durationMs") or {}).get("triggerExecution")
                    lags = []
                    for fte in p.get("sources", []):
                        v = (fte.get("metrics") or {}).get("maxOffsetsBehindLatest")
                        if v is not None:
                            try: lags.append(float(v))
                            except (TypeError, ValueError): pass
                    exc = q.exception()
                    cur.execute("""INSERT INTO metricas_pipeline (consulta,activa,batch_id,filas_entrada,duracion_ms,retraso_offsets,fecha_progreso_utc,observado_utc,error)
                      VALUES (%s,%s,%s,%s,%s,%s,%s,NOW(),%s) ON CONFLICT(consulta) DO UPDATE SET activa=EXCLUDED.activa,batch_id=EXCLUDED.batch_id,
                      filas_entrada=EXCLUDED.filas_entrada,duracion_ms=EXCLUDED.duracion_ms,retraso_offsets=EXCLUDED.retraso_offsets,
                      fecha_progreso_utc=EXCLUDED.fecha_progreso_utc,observado_utc=NOW(),error=EXCLUDED.error""",
                      (nombre, q.isActive, p.get("batchId"), p.get("numInputRows"), dur, max(lags) if lags else None,
                       p.get("timestamp"), str(exc) if exc else None))
        except Exception as exc:
            logging.warning("No pudo guardar métricas: %s", exc)
        stop.wait(10)


def main():
    preparar_db()
    for h in HORIZONTES:
        if not (ROOT / "modelos" / f"temperatura_{h}h").exists():
            raise FileNotFoundError(f"Entrena primero en Jupyter (cuaderno U2 de Mijael): falta modelos/temperatura_{h}h")
    spark = (SparkSession.builder.master("local[2]").appName("AgroSmart-U2-Consumer-Temperatura")
             .config("spark.sql.shuffle.partitions", "2").config("spark.sql.session.timeZone", "UTC").getOrCreate())
    spark.sparkContext.setLogLevel("WARN")
    modelos = {h: PipelineModel.load(str(ROOT / "modelos" / f"temperatura_{h}h")) for h in HORIZONTES}

    sensor_schema = T.StructType([T.StructField(n, T.StringType()) for n in ("evento_id", "fecha_evento", "emitido_utc", "ubicacion")]
        + [T.StructField("temperatura_c", T.DoubleType()), T.StructField("origen", T.StringType()), T.StructField("modo_publicacion", T.StringType())])
    emp_schema = T.StructType([T.StructField(n, T.StringType()) for n in ("evento_id", "evento_telemetria_id", "fecha_evento", "ubicacion", "tipo", "estado")]
        + [T.StructField("temperatura_c", T.DoubleType()), T.StructField("umbral_helada_c", T.DoubleType()), T.StructField("origen", T.StringType())])

    def leer(topic, schema):
        return (spark.readStream.format("kafka").option("kafka.bootstrap.servers", KAFKA).option("subscribe", topic)
                .option("startingOffsets", "earliest").option("failOnDataLoss", "true").load()
                .select("partition", "offset", F.from_json(F.col("value").cast("string"), schema).alias("dato"))
                .select("partition", "offset", "dato.*").withColumn("fecha_evento", F.to_timestamp("fecha_evento")))

    sensor = leer(TOPICO_SENSOR, sensor_schema).filter(
        F.col("evento_id").isNotNull() & F.col("fecha_evento").isNotNull() & F.col("emitido_utc").isNotNull()
        & F.col("ubicacion").isNotNull() & F.col("temperatura_c").between(-60.0, 60.0))
    negocio = leer(TOPICO_EMPRESA, emp_schema).filter(
        F.col("evento_id").isNotNull() & F.col("evento_telemetria_id").isNotNull() & F.col("fecha_evento").isNotNull()
        & F.col("temperatura_c").between(-60.0, 60.0))
    s_unico = sensor.withWatermark("fecha_evento", "2 hours").dropDuplicatesWithinWatermark(["evento_id"])
    e_unico = negocio.withWatermark("fecha_evento", "2 hours").dropDuplicatesWithinWatermark(["evento_id"])
    ventanas = (sensor.withWatermark("fecha_evento", "2 hours").groupBy(F.window("fecha_evento", "1 hour"), "ubicacion")
                .agg(F.count("*").alias("lecturas"), F.avg("temperatura_c").alias("media"),
                     F.min("temperatura_c").alias("minimo"), F.max("temperatura_c").alias("maximo")))

    def lote_sensor(df, batch_id):
        t0 = time.monotonic(); df.persist()
        try:
            filas = [(r.evento_id, hora_peru(r.fecha_evento), hora_peru(r.emitido_utc), r.ubicacion, r.temperatura_c, r.origen, r.modo_publicacion, r.partition, r.offset)
                     for r in df.toLocalIterator()]
            preds = []
            if filas:
                feats = (df.withColumn("hora_seno", F.sin(F.hour("fecha_evento") * F.lit(2 * math.pi / 24)))
                           .withColumn("hora_coseno", F.cos(F.hour("fecha_evento") * F.lit(2 * math.pi / 24))))
                for h, m in modelos.items():
                    for r in m.transform(feats).select("evento_id", "fecha_evento", "prediction").toLocalIterator():
                        evento = hora_peru(r.fecha_evento)
                        obj = evento + timedelta(hours=h)
                        preds.append((r.evento_id, h, evento, obj, float(r.prediction), m.stages[-1].__class__.__name__,
                                      datetime.now(timezone.utc) >= obj))
            with conexion() as conn, conn.cursor() as cur:
                guardar_lote("""INSERT INTO eventos_temperatura (evento_id,fecha_evento,emitido_utc,ubicacion,temperatura_c,origen,modo_publicacion,kafka_particion,kafka_offset)
                   VALUES %s ON CONFLICT(evento_id) DO NOTHING""", filas, cur)
                guardar_lote("""INSERT INTO predicciones_temperatura (evento_id,horizonte_h,fecha_evento,fecha_objetivo,prediccion_c,modelo,es_retro)
                   VALUES %s ON CONFLICT(evento_id,horizonte_h) DO NOTHING""", preds, cur)
            logging.info("S8/S10 temp_telemetria batch=%s filas=%s predicciones=%s duracion_s=%.2f", batch_id, len(filas), len(preds), time.monotonic() - t0)
        finally:
            df.unpersist()

    def lote_negocio(df, batch_id):
        filas = [(r.evento_id, r.evento_telemetria_id, hora_peru(r.fecha_evento), r.ubicacion, r.tipo, r.estado, r.temperatura_c, r.umbral_helada_c, r.origen)
                 for r in df.toLocalIterator()]
        with conexion() as conn, conn.cursor() as cur:
            guardar_lote("""INSERT INTO eventos_empresariales_temperatura (evento_id,evento_telemetria_id,fecha_evento,ubicacion,tipo,estado,temperatura_c,umbral_helada_c,origen)
               VALUES %s ON CONFLICT(evento_id) DO NOTHING""", filas, cur)
        logging.info("S6 temp_empresarial batch=%s filas=%s", batch_id, len(filas))

    def lote_ventanas(df, batch_id):
        filas = [(hora_peru(r.inicio), hora_peru(r.fin), r.ubicacion, r.lecturas, r.media, r.minimo, r.maximo)
                 for r in df.select(F.col("window.start").alias("inicio"), F.col("window.end").alias("fin"), "ubicacion", "lecturas", "media", "minimo", "maximo").toLocalIterator()]
        with conexion() as conn, conn.cursor() as cur:
            guardar_lote("""INSERT INTO ventanas_temperatura (inicio,fin,ubicacion,lecturas,temp_media_c,temp_min_c,temp_max_c)
               VALUES %s ON CONFLICT(inicio,fin,ubicacion) DO UPDATE SET lecturas=EXCLUDED.lecturas,temp_media_c=EXCLUDED.temp_media_c,
               temp_min_c=EXCLUDED.temp_min_c,temp_max_c=EXCLUDED.temp_max_c""", filas, cur)
        logging.info("S8 temp_ventanas batch=%s filas=%s", batch_id, len(filas))

    consultas = {}
    for nombre, df, fn, modo in [("temp_telemetria", s_unico, lote_sensor, "append"),
                                 ("temp_empresarial", e_unico, lote_negocio, "append"),
                                 ("temp_ventanas", ventanas, lote_ventanas, "update")]:
        q = (df.writeStream.queryName("agrosmart_" + nombre).outputMode(modo).foreachBatch(fn)
             .option("checkpointLocation", str(CP / nombre)).trigger(processingTime="5 seconds").start())
        consultas[nombre] = q
        logging.info("Consulta %s iniciada, id=%s", nombre, q.id)

    detener = threading.Event()
    hilo = threading.Thread(target=monitor_metricas, args=(consultas, detener), daemon=True); hilo.start()
    try:
        while True:
            malas = [(n, str(q.exception())) for n, q in consultas.items() if not q.isActive]
            if malas:
                raise RuntimeError(f"Consultas detenidas: {malas}")
            time.sleep(5)
    finally:
        detener.set(); hilo.join(timeout=20)
        for q in consultas.values():
            if q.isActive: q.stop()
        spark.stop()


if __name__ == "__main__":
    main()
