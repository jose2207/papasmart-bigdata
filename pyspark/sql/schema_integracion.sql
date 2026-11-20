-- U3 · DataOps: registro de cada ejecución integrada (equivale al manifiesto, consultable por Grafana/Prometheus). Idempotente.
CREATE TABLE IF NOT EXISTS ejecuciones_integracion (
 run_id TEXT PRIMARY KEY,
 ejecutado_utc TIMESTAMPTZ NOT NULL DEFAULT NOW(),
 estado TEXT NOT NULL CHECK (estado IN ('OK','ADVERTENCIA','FALLA')),
 compuertas_ok INTEGER NOT NULL,
 compuertas_total INTEGER NOT NULL,
 duracion_s DOUBLE PRECISION,
 lat_p50_hum_s DOUBLE PRECISION, lat_p95_hum_s DOUBLE PRECISION,
 lat_p50_temp_s DOUBLE PRECISION, lat_p95_temp_s DOUBLE PRECISION,
 eventos_hum INTEGER, eventos_temp INTEGER,
 pred_error_hum_1h DOUBLE PRECISION, pred_error_temp_1h DOUBLE PRECISION,
 manifiesto JSONB NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_ejec_int_fecha ON ejecuciones_integracion(ejecutado_utc DESC);
