# PySpark — entrenamiento Jupyter y Consumer Streaming separado

El profesor separa batch en notebooks y streaming persistente con `spark-submit`. Esta edición hace lo mismo:

- **Batch/MLlib en Jupyter:** `sesiones/Sensorhumedad/01_entrenamiento_y_verificacion_humedad.ipynb`. Solo Spark local, no conector Kafka, evita conflicto Ivy anterior.
- **Consumer persistente:** `scripts/consumer_streaming.py` vía `scripts/start_consumer.sh`, perfil `streaming` de `compose.kafka.yml`. Usa Spark 3.5.0, Kafka 4.x broker, paquete conector Spark Kafka `_2.12:3.5.0` y caché Ivy propia.
- **SQL:** `sql/schema.sql` crea tablas en PostgreSQL; también se aplica desde el notebook.
- **Costos:** `scripts/costos_pen.py`, suposición de tarifas directas en S/.

Iniciar Jupyter/DB:

```powershell
docker compose --env-file .env -f pyspark/compose.yml -f pyspark/compose.kafka.yml up -d --build postgres jupyter
```

**Después** de entrenar y guardar los tres modelos:

```powershell
docker compose --env-file .env -f pyspark/compose.yml -f pyspark/compose.kafka.yml --profile streaming up -d spark-consumer
docker compose --env-file .env -f pyspark/compose.yml -f pyspark/compose.kafka.yml logs -f spark-consumer
```

En `sensor`, `empresarial`, `ventanas` se reutilizan checkpoints separados de `sesiones/Sensorhumedad/checkpoints`; no los borres si deseas comprobar recuperación. Este es un laboratorio en un solo nodo, no un clúster productivo.
