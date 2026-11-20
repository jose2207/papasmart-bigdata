-- DIMENSIÓN DE MIJAEL: temperatura exterior (°C), zona de referencia Azángaro. Idempotente.
CREATE TABLE IF NOT EXISTS eventos_temperatura (
 evento_id TEXT PRIMARY KEY,
 fecha_evento TIMESTAMPTZ NOT NULL,
 emitido_utc TIMESTAMPTZ,
 ubicacion TEXT NOT NULL,
 temperatura_c DOUBLE PRECISION NOT NULL CHECK (temperatura_c BETWEEN -60 AND 60),
 origen TEXT NOT NULL,
 modo_publicacion TEXT,
 kafka_particion INTEGER,
 kafka_offset BIGINT,
 fecha_ingesta TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_temp_fecha ON eventos_temperatura(fecha_evento DESC);

CREATE TABLE IF NOT EXISTS eventos_empresariales_temperatura (
 evento_id TEXT PRIMARY KEY,
 evento_telemetria_id TEXT NOT NULL,
 fecha_evento TIMESTAMPTZ NOT NULL,
 ubicacion TEXT NOT NULL,
 tipo TEXT NOT NULL,
 estado TEXT NOT NULL,
 temperatura_c DOUBLE PRECISION NOT NULL,
 umbral_helada_c DOUBLE PRECISION,
 origen TEXT,
 fecha_registro TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_emp_temp_fecha ON eventos_empresariales_temperatura(fecha_evento DESC);

CREATE TABLE IF NOT EXISTS predicciones_temperatura (
 evento_id TEXT NOT NULL,
 horizonte_h INTEGER NOT NULL CHECK (horizonte_h IN (1,2,3)),
 fecha_evento TIMESTAMPTZ NOT NULL,
 fecha_objetivo TIMESTAMPTZ NOT NULL,
 prediccion_c DOUBLE PRECISION NOT NULL,
 modelo TEXT NOT NULL,
 es_retro BOOLEAN NOT NULL DEFAULT FALSE,
 fecha_registro TIMESTAMPTZ NOT NULL DEFAULT NOW(),
 PRIMARY KEY (evento_id, horizonte_h)
);
CREATE INDEX IF NOT EXISTS idx_pred_temp_fecha ON predicciones_temperatura(fecha_objetivo DESC);

CREATE TABLE IF NOT EXISTS ventanas_temperatura (
 inicio TIMESTAMPTZ NOT NULL,
 fin TIMESTAMPTZ NOT NULL,
 ubicacion TEXT NOT NULL,
 lecturas INTEGER NOT NULL,
 temp_media_c DOUBLE PRECISION,
 temp_min_c DOUBLE PRECISION,
 temp_max_c DOUBLE PRECISION,
 fecha_registro TIMESTAMPTZ NOT NULL DEFAULT NOW(),
 PRIMARY KEY (inicio, fin, ubicacion)
);

CREATE TABLE IF NOT EXISTS metricas_modelo_temperatura (
 horizonte_h INTEGER PRIMARY KEY CHECK (horizonte_h IN (1,2,3)),
 modelo TEXT NOT NULL,
 rmse DOUBLE PRECISION, mae DOUBLE PRECISION, r2 DOUBLE PRECISION,
 rmse_validacion DOUBLE PRECISION, baseline_rmse DOUBLE PRECISION,
 n_train INTEGER, n_validacion INTEGER, n_prueba INTEGER,
 fecha_registro TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS comparacion_modelos_temperatura (
 horizonte_h INTEGER NOT NULL CHECK (horizonte_h IN (1,2,3)),
 modelo TEXT NOT NULL,
 rmse_validacion DOUBLE PRECISION, rmse_prueba DOUBLE PRECISION,
 mae_prueba DOUBLE PRECISION, r2_prueba DOUBLE PRECISION,
 seleccionado BOOLEAN NOT NULL DEFAULT FALSE,
 fecha_registro TIMESTAMPTZ NOT NULL DEFAULT NOW(),
 PRIMARY KEY (horizonte_h, modelo)
);
