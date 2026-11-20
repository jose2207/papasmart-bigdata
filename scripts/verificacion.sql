SET timezone TO 'America/Lima';
\echo '=== Zona horaria y hora actual de la base ==='
SHOW timezone;
SELECT to_char(NOW(), 'DD/MM/YYYY HH24:MI:SS') AS hora_peru;

\echo '=== Conteo por tabla ==='
SELECT 'eventos_telemetria' AS tabla, COUNT(*) FROM eventos_telemetria
UNION ALL SELECT 'eventos_empresariales', COUNT(*) FROM eventos_empresariales
UNION ALL SELECT 'predicciones_humedad', COUNT(*) FROM predicciones_humedad
UNION ALL SELECT 'ventanas_humedad', COUNT(*) FROM ventanas_humedad
UNION ALL SELECT 'eventos_temperatura', COUNT(*) FROM eventos_temperatura
UNION ALL SELECT 'eventos_empresariales_temperatura', COUNT(*) FROM eventos_empresariales_temperatura
UNION ALL SELECT 'predicciones_temperatura', COUNT(*) FROM predicciones_temperatura
UNION ALL SELECT 'ventanas_temperatura', COUNT(*) FROM ventanas_temperatura
UNION ALL SELECT 'ejecuciones_integracion', COUNT(*) FROM ejecuciones_integracion;

\echo '=== Lecturas por origen (humedad) ==='
SELECT origen, COUNT(*) AS lecturas, to_char(MIN(fecha_evento),'DD/MM HH24:MI') AS primera, to_char(MAX(fecha_evento),'DD/MM HH24:MI') AS ultima
FROM eventos_telemetria GROUP BY origen ORDER BY 2 DESC;
\echo '=== Lecturas por origen (temperatura) ==='
SELECT origen, COUNT(*) AS lecturas, to_char(MIN(fecha_evento),'DD/MM HH24:MI') AS primera, to_char(MAX(fecha_evento),'DD/MM HH24:MI') AS ultima
FROM eventos_temperatura GROUP BY origen ORDER BY 2 DESC;

\echo '=== Desfase emision - evento en el flujo de 2 min (debe ser de segundos) ==='
SELECT 'humedad' AS dim, ROUND(percentile_cont(0.5) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM emitido_utc - fecha_evento))::numeric) AS mediana_s
FROM eventos_telemetria WHERE origen='open_meteo_interpolado_2min' AND fecha_evento > NOW() - INTERVAL '1 hour'
UNION ALL
SELECT 'temperatura', ROUND(percentile_cont(0.5) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM emitido_utc - fecha_evento))::numeric)
FROM eventos_temperatura WHERE origen='open_meteo_interpolado_2min' AND fecha_evento > NOW() - INTERVAL '1 hour';

\echo '=== Ultimas lecturas y sus predicciones (humedad, hora de Peru) ==='
SELECT to_char(t.fecha_evento,'DD/MM HH24:MI') AS evento, ROUND(t.humedad_suelo_pct::numeric,3) AS suelo_pct, p.horizonte_h AS h,
       to_char(p.fecha_objetivo,'DD/MM HH24:MI') AS objetivo, ROUND(p.prediccion_pct::numeric,3) AS pred_pct, p.es_retro, p.modelo
FROM eventos_telemetria t JOIN predicciones_humedad p USING (evento_id)
ORDER BY t.fecha_evento DESC, p.horizonte_h LIMIT 9;
\echo '=== Ultimas lecturas y sus predicciones (temperatura, hora de Peru) ==='
SELECT to_char(t.fecha_evento,'DD/MM HH24:MI') AS evento, ROUND(t.temperatura_c::numeric,2) AS temp_c, p.horizonte_h AS h,
       to_char(p.fecha_objetivo,'DD/MM HH24:MI') AS objetivo, ROUND(p.prediccion_c::numeric,2) AS pred_c, p.es_retro, p.modelo
FROM eventos_temperatura t JOIN predicciones_temperatura p USING (evento_id)
ORDER BY t.fecha_evento DESC LIMIT 5;

\echo '=== Error en produccion: prediccion +1 h vs lectura real (ultimas 24 h) ==='
WITH par AS (
  SELECT p.horizonte_h, p.prediccion_pct AS pred, t2.humedad_suelo_pct AS real, ant.humedad_suelo_pct AS persist
  FROM predicciones_humedad p
  JOIN eventos_telemetria ant ON ant.evento_id = p.evento_id
  JOIN LATERAL (SELECT humedad_suelo_pct FROM eventos_telemetria x
                WHERE x.fecha_evento BETWEEN p.fecha_objetivo - INTERVAL '1 minute' AND p.fecha_objetivo + INTERVAL '1 minute'
                ORDER BY ABS(EXTRACT(EPOCH FROM x.fecha_evento - p.fecha_objetivo)) LIMIT 1) t2 ON TRUE
  WHERE p.fecha_objetivo > NOW() - INTERVAL '24 hours' AND p.fecha_objetivo <= NOW())
SELECT 'humedad' AS dim, horizonte_h AS h, COUNT(*) AS n,
       ROUND(SQRT(AVG((pred-real)^2))::numeric,4) AS rmse_modelo, ROUND(SQRT(AVG((persist-real)^2))::numeric,4) AS rmse_persistencia
FROM par GROUP BY horizonte_h ORDER BY 2;
WITH par AS (
  SELECT p.prediccion_c AS pred, t2.temperatura_c AS real, ant.temperatura_c AS persist
  FROM predicciones_temperatura p
  JOIN eventos_temperatura ant ON ant.evento_id = p.evento_id
  JOIN LATERAL (SELECT temperatura_c FROM eventos_temperatura x
                WHERE x.fecha_evento BETWEEN p.fecha_objetivo - INTERVAL '1 minute' AND p.fecha_objetivo + INTERVAL '1 minute'
                ORDER BY ABS(EXTRACT(EPOCH FROM x.fecha_evento - p.fecha_objetivo)) LIMIT 1) t2 ON TRUE
  WHERE p.fecha_objetivo > NOW() - INTERVAL '24 hours' AND p.fecha_objetivo <= NOW())
SELECT 'temperatura' AS dim, 1 AS h, COUNT(*) AS n,
       ROUND(SQRT(AVG((pred-real)^2))::numeric,4) AS rmse_modelo, ROUND(SQRT(AVG((persist-real)^2))::numeric,4) AS rmse_persistencia FROM par;

\echo '=== Consultas Spark (heartbeat) ==='
SELECT consulta, activa, batch_id, filas_entrada, ROUND(duracion_ms::numeric) AS duracion_ms,
       to_char(observado_utc,'DD/MM HH24:MI:SS') AS observado, error FROM metricas_pipeline ORDER BY consulta;

\echo '=== Ventanas de 1 h mas recientes ==='
SELECT to_char(inicio,'DD/MM HH24:MI') AS inicio, to_char(fin,'HH24:MI') AS fin, lecturas, ROUND(humedad_suelo_media_pct::numeric,3) AS suelo_media
FROM ventanas_humedad ORDER BY inicio DESC LIMIT 3;
SELECT to_char(inicio,'DD/MM HH24:MI') AS inicio, to_char(fin,'HH24:MI') AS fin, lecturas, ROUND(temp_media_c::numeric,2) AS media, ROUND(temp_min_c::numeric,2) AS minima, ROUND(temp_max_c::numeric,2) AS maxima
FROM ventanas_temperatura ORDER BY inicio DESC LIMIT 3;

\echo '=== Evaluaciones empresariales por estado ==='
SELECT 'humedad' AS dim, estado, COUNT(*) FROM eventos_empresariales GROUP BY estado
UNION ALL SELECT 'temperatura', estado, COUNT(*) FROM eventos_empresariales_temperatura GROUP BY estado ORDER BY 1,3 DESC;

\echo '=== Modelos registrados ==='
SELECT 'humedad' AS dim, horizonte_h, modelo, ROUND(rmse::numeric,4) AS rmse, ROUND(baseline_rmse::numeric,4) AS persistencia FROM metricas_modelo
UNION ALL SELECT 'temperatura', horizonte_h, modelo, ROUND(rmse::numeric,4), ROUND(baseline_rmse::numeric,4) FROM metricas_modelo_temperatura ORDER BY 1,2;

\echo '=== Ejecuciones integradas (DataOps) ==='
SELECT to_char(ejecutado_utc,'DD/MM HH24:MI') AS fecha, run_id, estado, compuertas_ok || '/' || compuertas_total AS compuertas FROM ejecuciones_integracion ORDER BY ejecutado_utc DESC LIMIT 5;

\echo '=== Tamano de la base ==='
SELECT pg_size_pretty(pg_database_size(current_database())) AS tamano_bd;
