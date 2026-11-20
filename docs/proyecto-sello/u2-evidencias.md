# Bitácora de evidencias S6–S12

Marcar **solo después** de verificar cada prueba. No reemplazar capturas por datos inventados.

| Prueba | Archivo o captura a guardar | Estado (19-nov-2026) |
|---|---|---|
| Kafka empresarial S6 | UI tópico `...empresarial`, mensaje/offset y consumidor de verificación | Verificado: offset 1 333 en `…-empresarial`; 1 347 + 1 263 evaluaciones en PostgreSQL |
| API telemetría S7 | consulta con 2 variables, UTC, número de registros y unidades | Verificado: 3 orígenes etiquetados (simulado, modelado, interpolado 2 min) |
| Kafka IoT S7 | UI tópico `...telemetria`, volumen y offsets | Verificado: offsets 1 333 en los tópicos de telemetría; consumer de verificación |
| Spark S8 | logs de tres consultas activas sin errores + offsets procesados | Verificado: 6 consultas activas (heartbeat) y logs sin errores |
| Watermark S8 | mensaje tardío publicado y consulta SQL de ID descartado (si efectivamente sucede) | Pendiente |
| Checkpoint S8 | tres directorios checkpoint y prueba de reinicio sin duplicados | Verificado: reinicio de los consumers el 19-nov; el batchId siguió numerando desde el checkpoint (975 a las 16:38 → 1029 tras el reinicio) y `evento_id` sigue sin duplicados (compuerta de calidad) |
| Observabilidad S9 | Prometheus Targets UP y series de filas/duración/heartbeat | Verificado: targets UP, series por consulta |
| Alertas S9 | Normal → Pending → Firing → Normal y explicación del disparo | Pendiente |
| Costos S9 | `docker stats`, tabla `escenarios_costos` y archivo `costos_pen.json` en soles | Verificado: `docker stats` en `evidencias/verificacion_ultima.txt` y `costos_pen.json` |
| ML S10 | 12 resultados, 3 ganadores, RMSE/MAE/R², baseline y modelo cargado | Verificado: `metricas_modelo*.csv` y modelos cargados por los consumers |
| Predicción S10 | tabla `predicciones_humedad`, campo `es_retro`, objetivo +1/2/3 | Verificado: objetivo = evento + h, `es_retro = f` en vivo (tras la corrección de hora) |
| BI S11 | un solo screenshot de Grafana con KPI + humedad + predicción | Verificado: dashboard v4 en 3 partes |
| Sustentación S12 | enlace MkDocs, repositorio, commits, topics, PPT y demo individual | Pendiente |

## Protocolo de demo defendible

1. Mostrar JSON de API y señalar que es **modelado**, no sensor físico.
2. Abrir Kafka UI: tópicos y consumer `consumer_verificacion.py` / `consumer_verificacion_empresa.py` con offsets.
3. Mostrar `spark-consumer` persistente con sus tres consultas y checkpoints.
4. Publicar una tanda de replay delante del docente; comprobar nueva llegada a Kafka y persistencia PostgreSQL. Repetir IDs para verificar idempotencia.
5. Mostrar prueba de un evento tardío, esperar progreso y cotejar el ID en SQL.
6. Prometheus Targets UP, dashboard Grafana completo; explicar fechas en replay histórico y campo `es_retro`.
7. Enseñar 12 evaluaciones ML, RMSE/MAE/R², baseline y 3 modelos guardados.
8. Mostrar costos en S/ como escenario, con tasas/mediciones justificadas.
9. Terminar con GitHub y documentación pública; sustentar el aporte individual.

## Dos fortalezas y dos oportunidades para Unidad III

**Fortalezas esperadas a comprobar:** arquitectura modular con producer/consumer independientes; modelos separados con selección temporal y métricas reproducibles. **Siguientes pasos recomendados:** contrastar Open-Meteo con sondas físicas del suelo; ampliar pruebas de despliegue, carga, fallos y monitoreo a volúmenes mayores.
