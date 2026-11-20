-- =====================================================================================
-- AgroSmart Puno · Reparación de hora (Perú, UTC-5)
-- Antes de la corrección, los consumidores Spark guardaban los timestamps 5 h atrasados
-- (PySpark entrega la hora local sin zona y el código la trataba como UTC).
-- Este script:
--   1) pone la base en hora de Perú (America/Lima) para todas las consultas;
--   2) MIDE el desfase con el flujo cada 2 min (emitido_utc se guardó bien porque es texto);
--   3) SOLO si el desfase mediano está entre 4,5 y 5,5 h, suma 5 h a lo escrito por Spark.
-- Es seguro ejecutarlo más de una vez: si ya no hay desfase, no cambia nada.
-- IMPORTANTE: detén los consumidores Spark antes de ejecutarlo.
-- =====================================================================================
DO $$ BEGIN EXECUTE format('ALTER DATABASE %I SET timezone TO %L', current_database(), 'America/Lima'); END $$;
SET timezone TO 'America/Lima';

\echo '--- Desfase ANTES (segundos entre emisión y fecha del evento, flujo cada 2 min) ---'
SELECT 'humedad' AS dimension, COUNT(*) AS eventos,
       ROUND(percentile_cont(0.5) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM emitido_utc - fecha_evento))::numeric) AS desfase_mediano_s
FROM eventos_telemetria WHERE origen = 'open_meteo_interpolado_2min'
UNION ALL
SELECT 'temperatura', COUNT(*),
       ROUND(percentile_cont(0.5) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM emitido_utc - fecha_evento))::numeric)
FROM eventos_temperatura WHERE origen = 'open_meteo_interpolado_2min';

BEGIN;
DO $$
DECLARE d double precision; n bigint;
BEGIN
  -- ============================== HUMEDAD ==============================
  SELECT percentile_cont(0.5) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM emitido_utc - fecha_evento))
    INTO d FROM eventos_telemetria WHERE origen = 'open_meteo_interpolado_2min';
  IF d BETWEEN 16200 AND 19800 THEN
    CREATE TEMP TABLE ids_h ON COMMIT DROP AS
      SELECT evento_id FROM eventos_telemetria WHERE kafka_offset IS NOT NULL;
    UPDATE eventos_telemetria SET fecha_evento = fecha_evento + INTERVAL '5 hours'
      WHERE evento_id IN (SELECT evento_id FROM ids_h);
    GET DIAGNOSTICS n = ROW_COUNT; RAISE NOTICE 'humedad · lecturas corregidas: %', n;
    UPDATE predicciones_humedad SET fecha_evento = fecha_evento + INTERVAL '5 hours',
           fecha_objetivo = fecha_objetivo + INTERVAL '5 hours'
      WHERE evento_id IN (SELECT evento_id FROM ids_h);
    UPDATE predicciones_humedad SET es_retro = (generado_utc >= fecha_objetivo);
    GET DIAGNOSTICS n = ROW_COUNT; RAISE NOTICE 'humedad · predicciones recalculadas: %', n;
    UPDATE eventos_empresariales SET fecha_evento = fecha_evento + INTERVAL '5 hours';
    CREATE TEMP TABLE v_h ON COMMIT DROP AS SELECT * FROM ventanas_humedad;
    DELETE FROM ventanas_humedad;
    INSERT INTO ventanas_humedad (inicio, fin, ubicacion, lecturas, humedad_suelo_media_pct, humedad_aire_media_pct)
      SELECT inicio + INTERVAL '5 hours', fin + INTERVAL '5 hours', ubicacion, lecturas, humedad_suelo_media_pct, humedad_aire_media_pct FROM v_h;
    RAISE NOTICE 'humedad · eventos empresariales y ventanas corregidos';
  ELSE
    RAISE NOTICE 'humedad · sin desfase de 5 h (mediana % s): no se cambia nada', COALESCE(round(d::numeric), -1);
  END IF;

  -- ============================== TEMPERATURA ==============================
  SELECT percentile_cont(0.5) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM emitido_utc - fecha_evento))
    INTO d FROM eventos_temperatura WHERE origen = 'open_meteo_interpolado_2min';
  IF d BETWEEN 16200 AND 19800 THEN
    CREATE TEMP TABLE ids_t ON COMMIT DROP AS
      SELECT evento_id FROM eventos_temperatura WHERE kafka_offset IS NOT NULL;
    UPDATE eventos_temperatura SET fecha_evento = fecha_evento + INTERVAL '5 hours'
      WHERE evento_id IN (SELECT evento_id FROM ids_t);
    GET DIAGNOSTICS n = ROW_COUNT; RAISE NOTICE 'temperatura · lecturas corregidas: %', n;
    UPDATE predicciones_temperatura SET fecha_evento = fecha_evento + INTERVAL '5 hours',
           fecha_objetivo = fecha_objetivo + INTERVAL '5 hours'
      WHERE evento_id IN (SELECT evento_id FROM ids_t);
    UPDATE predicciones_temperatura SET es_retro = (fecha_registro >= fecha_objetivo);
    GET DIAGNOSTICS n = ROW_COUNT; RAISE NOTICE 'temperatura · predicciones recalculadas: %', n;
    UPDATE eventos_empresariales_temperatura SET fecha_evento = fecha_evento + INTERVAL '5 hours';
    CREATE TEMP TABLE v_t ON COMMIT DROP AS SELECT * FROM ventanas_temperatura;
    DELETE FROM ventanas_temperatura;
    INSERT INTO ventanas_temperatura (inicio, fin, ubicacion, lecturas, temp_media_c, temp_min_c, temp_max_c, fecha_registro)
      SELECT inicio + INTERVAL '5 hours', fin + INTERVAL '5 hours', ubicacion, lecturas, temp_media_c, temp_min_c, temp_max_c, fecha_registro FROM v_t;
    RAISE NOTICE 'temperatura · evaluaciones y ventanas corregidas';
  ELSE
    RAISE NOTICE 'temperatura · sin desfase de 5 h (mediana % s): no se cambia nada', COALESCE(round(d::numeric), -1);
  END IF;
END $$;
COMMIT;

\echo '--- DESPUÉS: últimos eventos y sus predicciones (hora de Perú) ---'
SELECT to_char(t.fecha_evento, 'DD/MM HH24:MI') AS evento, p.horizonte_h AS h,
       to_char(p.fecha_objetivo, 'DD/MM HH24:MI') AS objetivo, ROUND(p.prediccion_pct::numeric, 2) AS pred_pct, p.es_retro
FROM eventos_telemetria t JOIN predicciones_humedad p USING (evento_id)
ORDER BY t.fecha_evento DESC, p.horizonte_h LIMIT 6;
SELECT to_char(t.fecha_evento, 'DD/MM HH24:MI') AS evento, p.horizonte_h AS h,
       to_char(p.fecha_objetivo, 'DD/MM HH24:MI') AS objetivo, ROUND(p.prediccion_c::numeric, 2) AS pred_c, p.es_retro
FROM eventos_temperatura t JOIN predicciones_temperatura p USING (evento_id)
ORDER BY t.fecha_evento DESC LIMIT 3;
SELECT NOW() AS hora_actual_peru;
