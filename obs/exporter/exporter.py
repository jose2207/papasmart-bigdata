"""Puente de métricas de PostgreSQL a Prometheus.
El exportador NO mide realmente el lag cuando Spark no lo reporta: dato ausente
se omite (no se convierte en cero). Monitoreo de consultas por heartbeat.
"""
import logging
import os
import time
from contextlib import closing
import psycopg2
from prometheus_client import Gauge, start_http_server

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
OK=Gauge('agrosmart_exportador_consulta_ok','1 si PostgreSQL respondió con tablas esperadas')
TELEM=Gauge('agrosmart_telemetria_registros','Filas válidas guardadas por consumidor Spark')
EMP=Gauge('agrosmart_empresarial_eventos','Eventos empresariales simulados guardados')
PRED=Gauge('agrosmart_predicciones_registros','Predicciones ML registradas')
WIN=Gauge('agrosmart_ventanas_registros','Ventanas agregadas guardadas')
ACTIVE=Gauge('agrosmart_consulta_activa','1 si la consulta Spark estaba activa en el ultimo heartbeat',['consulta'])
ROWS=Gauge('agrosmart_filas_ultimo_lote','Filas del ultimo microlote',['consulta'])
DURATION=Gauge('agrosmart_duracion_lote_ms','Duracion ultimo microlote, milisegundos',['consulta'])
LAG=Gauge('agrosmart_retraso_offsets','Lag reportado por Spark, si esta disponible',['consulta'])
AGE=Gauge('agrosmart_edad_heartbeat_segundos','Segundos desde ultimo estado observado Spark',['consulta'])
ERR=Gauge('agrosmart_consulta_error','1 si la consulta registro error',['consulta'])
MODELRMSE=Gauge('agrosmart_modelo_rmse','RMSE prueba por horizonte, puntos porcentuales',['horizonte_h'])
# --- Dimensión de Mijael (temperatura) ---
TEMP_TELEM=Gauge('agrosmart_temperatura_registros','Lecturas de temperatura guardadas por Spark')
TEMP_EMP=Gauge('agrosmart_temperatura_evaluaciones','Evaluaciones de riesgo de helada simuladas guardadas')
TEMP_PRED=Gauge('agrosmart_temperatura_predicciones','Predicciones de temperatura registradas')
TEMP_WIN=Gauge('agrosmart_temperatura_ventanas','Ventanas de temperatura guardadas')
INT_AGE=Gauge('agrosmart_int_ultima_ejecucion_edad_segundos','Segundos desde la última ejecución integrada (DataOps)')
INT_GATES=Gauge('agrosmart_int_compuertas_ok_ratio','Fracción de compuertas aprobadas en la última ejecución integrada')
INT_STATE=Gauge('agrosmart_int_ultima_ejecucion_estado','0=OK, 1=ADVERTENCIA, 2=FALLA')
INT_LAT=Gauge('agrosmart_int_latencia_pipeline_segundos','Latencia extremo a extremo del pipeline (percentil) por dimensión',['dimension','percentil'])
INT_ERR=Gauge('agrosmart_int_error_prediccion_1h','Error absoluto medio de la predicción a +1 h observado en producción',['dimension'])
TEMP_RMSE=Gauge('agrosmart_temperatura_modelo_rmse','RMSE de prueba del modelo de temperatura, grados Celsius',['horizonte_h'])

def conexion():
    return psycopg2.connect(host=os.getenv('POSTGRES_HOST','postgres'),
        dbname=os.getenv('POSTGRES_DB','agrosmart_u2'),
        user=os.getenv('POSTGRES_USER','agrosmart'),
        password=os.environ['POSTGRES_PASSWORD'],connect_timeout=5)

def obtener():
    with closing(conexion()) as conn, conn.cursor() as cur:
        cur.execute("SELECT to_regclass('public.eventos_telemetria')")
        if cur.fetchone()[0] is None:
            OK.set(0)
            return
        for tabla,metrica in [
            ('eventos_telemetria',TELEM),('eventos_empresariales',EMP),
            ('predicciones_humedad',PRED),('ventanas_humedad',WIN)]:
            cur.execute('SELECT COUNT(*) FROM '+tabla)
            metrica.set(cur.fetchone()[0])
        cur.execute('''SELECT consulta,activa,filas_entrada,duracion_ms,retraso_offsets,
          EXTRACT(EPOCH FROM(NOW()-observado_utc)), error FROM metricas_pipeline''')
        for nombre,activo,filas,ms,lag,edad,error in cur.fetchall():
            ACTIVE.labels(nombre).set(int(activo))
            if filas is not None: ROWS.labels(nombre).set(filas)
            if ms is not None: DURATION.labels(nombre).set(ms)
            if lag is not None: LAG.labels(nombre).set(lag)
            AGE.labels(nombre).set(max(0.0,float(edad or 0)))
            ERR.labels(nombre).set(1 if error else 0)
        cur.execute('SELECT horizonte_h,rmse FROM metricas_modelo WHERE rmse IS NOT NULL')
        for horizonte,rmse in cur.fetchall():
            MODELRMSE.labels(str(horizonte)).set(rmse)
        # Temperatura (Mijael): opcional, no rompe la lectura de humedad si aún no existe
        cur.execute("SELECT to_regclass('public.eventos_temperatura')")
        if cur.fetchone()[0] is not None:
            for tabla,metrica in [('eventos_temperatura',TEMP_TELEM),('eventos_empresariales_temperatura',TEMP_EMP),
                                  ('predicciones_temperatura',TEMP_PRED),('ventanas_temperatura',TEMP_WIN)]:
                cur.execute('SELECT COUNT(*) FROM '+tabla)
                metrica.set(cur.fetchone()[0])
            cur.execute('SELECT horizonte_h,rmse FROM metricas_modelo_temperatura WHERE rmse IS NOT NULL')
            for horizonte,rmse in cur.fetchall():
                TEMP_RMSE.labels(str(horizonte)).set(rmse)
        # DataOps U3: última ejecución integrada (opcional)
        cur.execute("SELECT to_regclass('public.ejecuciones_integracion')")
        if cur.fetchone()[0] is not None:
            cur.execute('''SELECT EXTRACT(EPOCH FROM (NOW()-ejecutado_utc)), compuertas_ok, compuertas_total, estado,
                           lat_p50_hum_s, lat_p95_hum_s, lat_p50_temp_s, lat_p95_temp_s, pred_error_hum_1h, pred_error_temp_1h
                           FROM ejecuciones_integracion ORDER BY ejecutado_utc DESC LIMIT 1''')
            fila = cur.fetchone()
            if fila:
                edad, ok, total, estado, h50, h95, t50, t95, eh, et = fila
                INT_AGE.set(float(edad)); INT_GATES.set(ok/max(1,total)); INT_STATE.set({'OK':0,'ADVERTENCIA':1,'FALLA':2}[estado])
                for dim,p50,p95,err in (('humedad',h50,h95,eh),('temperatura',t50,t95,et)):
                    if p50 is not None: INT_LAT.labels(dim,'p50').set(p50)
                    if p95 is not None: INT_LAT.labels(dim,'p95').set(p95)
                    if err is not None: INT_ERR.labels(dim).set(err)
    OK.set(1)

if __name__=='__main__':
    start_http_server(9200,addr='0.0.0.0')
    while True:
        try: obtener()
        except Exception as exc:
            OK.set(0)
            logging.warning('No se pudo consultar PostgreSQL: %s',exc)
        time.sleep(10)
