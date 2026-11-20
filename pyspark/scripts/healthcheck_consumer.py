"""Healthcheck de un consumer Spark: 'sano' = su consulta reporta activa en metricas_pipeline en los últimos 90 s.
Uso (Docker): python /opt/agrosmart-scripts/healthcheck_consumer.py telemetria   |   temp_telemetria
"""
import os, sys
import psycopg2

consulta = sys.argv[1] if len(sys.argv) > 1 else "telemetria"
try:
    con = psycopg2.connect(host=os.getenv("POSTGRES_HOST", "postgres"), dbname=os.environ["POSTGRES_DB"], user=os.environ["POSTGRES_USER"],
                           password=os.environ["POSTGRES_PASSWORD"], connect_timeout=5)
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM metricas_pipeline WHERE consulta=%s AND activa AND error IS NULL AND observado_utc > NOW() - INTERVAL '90 seconds'", (consulta,))
    sys.exit(0 if cur.fetchone()[0] == 1 else 1)
except Exception as exc:
    print("healthcheck falló:", exc)
    sys.exit(1)
