-- AgroSmart Puno U2. PostgreSQL 16. Todos los valores son de la dimensión humedad.
CREATE TABLE IF NOT EXISTS eventos_telemetria (
 evento_id TEXT PRIMARY KEY,
 fecha_evento TIMESTAMPTZ NOT NULL,
 emitido_utc TIMESTAMPTZ NOT NULL,
 ingestado_utc TIMESTAMPTZ NOT NULL DEFAULT NOW(),
 ubicacion TEXT NOT NULL,
 humedad_suelo_m3m3 DOUBLE PRECISION NOT NULL CHECK(humedad_suelo_m3m3 BETWEEN 0 AND 1),
 humedad_suelo_pct DOUBLE PRECISION NOT NULL CHECK(humedad_suelo_pct BETWEEN 0 AND 100),
 humedad_aire_pct DOUBLE PRECISION NOT NULL CHECK(humedad_aire_pct BETWEEN 0 AND 100),
 origen TEXT NOT NULL,
 modo_publicacion TEXT NOT NULL,
 kafka_particion INTEGER,
 kafka_offset BIGINT
);
CREATE INDEX IF NOT EXISTS idx_telemetria_fecha ON eventos_telemetria(fecha_evento DESC);

CREATE TABLE IF NOT EXISTS eventos_empresariales (
 evento_id TEXT PRIMARY KEY,
 evento_telemetria_id TEXT NOT NULL,
 fecha_evento TIMESTAMPTZ NOT NULL,
 recibido_utc TIMESTAMPTZ NOT NULL DEFAULT NOW(),
 ubicacion TEXT NOT NULL,
 tipo TEXT NOT NULL,
 estado TEXT NOT NULL,
 humedad_suelo_pct DOUBLE PRECISION NOT NULL,
 humedad_aire_pct DOUBLE PRECISION NOT NULL,
 umbral_demo_pct DOUBLE PRECISION NOT NULL,
 origen TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_empresarial_fecha ON eventos_empresariales(fecha_evento DESC);

CREATE TABLE IF NOT EXISTS predicciones_humedad (
 evento_id TEXT NOT NULL,
 horizonte_h INTEGER NOT NULL CHECK (horizonte_h IN (1,2,3)),
 fecha_evento TIMESTAMPTZ NOT NULL,
 fecha_objetivo TIMESTAMPTZ NOT NULL,
 generado_utc TIMESTAMPTZ NOT NULL DEFAULT NOW(),
 prediccion_pct DOUBLE PRECISION NOT NULL,
 modelo TEXT NOT NULL,
 es_retro BOOLEAN NOT NULL,
 PRIMARY KEY (evento_id,horizonte_h)
);
CREATE INDEX IF NOT EXISTS idx_pred_fecha ON predicciones_humedad(fecha_objetivo DESC);

CREATE TABLE IF NOT EXISTS ventanas_humedad (
 inicio TIMESTAMPTZ NOT NULL,
 fin TIMESTAMPTZ NOT NULL,
 ubicacion TEXT NOT NULL,
 lecturas BIGINT NOT NULL,
 humedad_suelo_media_pct DOUBLE PRECISION,
 humedad_aire_media_pct DOUBLE PRECISION,
 PRIMARY KEY (inicio,fin,ubicacion)
);

CREATE TABLE IF NOT EXISTS metricas_modelo (
 horizonte_h INTEGER PRIMARY KEY CHECK (horizonte_h IN (1,2,3)),
 modelo TEXT NOT NULL,
 rmse DOUBLE PRECISION,
 mae DOUBLE PRECISION,
 r2 DOUBLE PRECISION,
 rmse_validacion DOUBLE PRECISION,
 baseline_rmse DOUBLE PRECISION,
 n_train INTEGER NOT NULL,
 n_validacion INTEGER NOT NULL,
 n_prueba INTEGER NOT NULL,
 fecha_registro TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS metricas_pipeline (
 consulta TEXT PRIMARY KEY,
 activa BOOLEAN NOT NULL DEFAULT FALSE,
 batch_id BIGINT,
 filas_entrada BIGINT,
 duracion_ms DOUBLE PRECISION,
 retraso_offsets DOUBLE PRECISION,
 fecha_progreso_utc TIMESTAMPTZ,
 observado_utc TIMESTAMPTZ NOT NULL DEFAULT NOW(),
 error TEXT
);

CREATE TABLE IF NOT EXISTS escenarios_costos (
 nombre TEXT PRIMARY KEY,
 eventos_hora INTEGER NOT NULL,
 eventos_mes INTEGER NOT NULL,
 almacenamiento_gb DOUBLE PRECISION NOT NULL,
 computo_pen DOUBLE PRECISION NOT NULL,
 almacenamiento_pen DOUBLE PRECISION NOT NULL,
 total_pen DOUBLE PRECISION NOT NULL,
 fecha_calculo TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS comparacion_modelos (
 horizonte_h INTEGER NOT NULL,
 modelo TEXT NOT NULL,
 rmse_validacion DOUBLE PRECISION,
 rmse_prueba DOUBLE PRECISION,
 mae_prueba DOUBLE PRECISION,
 r2_prueba DOUBLE PRECISION,
 seleccionado BOOLEAN NOT NULL,
 fecha_registro TIMESTAMPTZ NOT NULL DEFAULT NOW(),
 PRIMARY KEY(horizonte_h,modelo)
);
