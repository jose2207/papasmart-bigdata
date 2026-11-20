# S8 · Procesamiento en streaming

**José · DimensiónU2.** Esta sesión aporta al monitoreo y predicción en tiempo real de la humedad.

`pyspark/scripts/consumer_streaming.py` se ejecuta persistente con `spark-submit`, no como celdas dependientes de la sesión Jupyter. Consume dos tópicos y genera tres consultas:

1. `telemetria`: valida rangos, hace watermark 2 h y `dropDuplicatesWithinWatermark(evento_id)`; escribe eventos y predicciones con `ON CONFLICT`.
2. `empresarial`: valida y deduplica evaluaciones de humedad; escribe PostgreSQL.
3. `ventanas`: `groupBy(window(fecha_evento,"1 hour"),ubicacion)`; media suelo, aire y conteo con watermark 2 h, modo `update`.

Cada consulta tiene checkpoint en carpeta distinta. Para probar tardíos, publicar primero los registros ordenados, esperar que avance el watermark y publicar después una estimación antigua con ID nuevo. No afirmar que fue descartada sin revisar la tabla SQL. En un proyecto de mayor escala, el sink `foreachBatch` debe reemplazarse por un sink particionado/optimizado para volúmenes mayores.
