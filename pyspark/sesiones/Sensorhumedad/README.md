# Carpeta Jupyter — dimensión U2 de José

Notebook principal: **`01_entrenamiento_y_verificacion_humedad.ipynb`**.

1. Inicia Kafka y Jupyter/DB desde raíz (ver README principal).
2. Ejecuta las etapas 0–4 del notebook: descarga 60 días de Open-Meteo, inspecciona dos series de humedad, compara cuatro modelos × tres horizontes, guarda 3 modelos y métricas en PostgreSQL.
3. Desde PowerShell inicia Consumer Spark persistente, `producer-evaluaciones` y `producer-api-replay`.
4. Regresa a la etapa 6 para consultar las tablas; observa PostgreSQL, Prometheus y Grafana.
5. Guarda capturas de resultados reales en `evidencias/`; evita publicar credenciales.

**No ejecutes dos consumidores Spark simultáneamente con los mismos checkpoints.** No borres checkpoints/modelos para repetir una demo que requiera recuperación.
