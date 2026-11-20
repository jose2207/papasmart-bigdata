# Matriz de trazabilidad

Relaciona la **variable** y su **pregunta** con la **dimensión de cada integrante**, sus indicadores **U1 (batch)** y **U2 (streaming)**, el componente y la técnica, y la **evidencia**. Una fila por indicador y por integrante.

**Variable:** condiciones meteorológicas de riesgo agrícola en el altiplano de Puno.
**Pregunta central:** ¿cómo anticipar a corto plazo las condiciones meteorológicas de riesgo agrícola del altiplano de Puno —estrés hídrico del suelo y heladas— a partir de datos de Open-Meteo?

| Nivel | Pregunta | Indicador | Componente y técnica | Evidencia |
|---|---|---|---|---|
| **José · Dimensión: humedad del suelo · U1 (batch)** | ¿Cuánta humedad del suelo explican la humedad del aire y la hora, y qué humedad cabe esperar? | RMSE/MAE/R² del mejor modelo frente al baseline; humedad esperada (foto fija); filas Bronze→Silver, −999 y duplicados | PySpark (lazy evaluation, ventanas, RDD), calidad de datos, Parquet por `anio_mes`, MLlib (Lineal, Ridge, Elastic Net, RF, GBT) y ablación | Cuaderno `U1_AgroSmart_S01_S05_Humedad_Batch.ipynb`; `resumen_u1.json` |
| **José · U2 (streaming)** | ¿Qué humedad del suelo habrá en Puno a +1, +2 y +3 h? | Humedad en vivo; RMSE/MAE/R² por horizonte frente a persistencia (prueba = datos reales de la API) | Kafka (2 tópicos), Spark Structured Streaming (ventana 1 h, watermark 2 h, checkpoints), MLlib series de tiempo (4 algoritmos × 3 horizontes) | Cuaderno U2; `metricas_modelo.csv`; Grafana filas 01–06 |
| **Mijael · Dimensión: temperatura exterior (Azángaro) · U1 (batch)** | ¿Cuántas horas de helada y qué temperatura cabe esperar una hora después? | Mín/máx/media diaria, horas ≤ 0 °C; RMSE/MAE/R² frente a persistencia; imputadas con respaldo | PySpark (lag/lead, ventanas), imputación con fuente de respaldo, Parquet, MLlib con división cronológica y ablación | Cuaderno `U1_Mijael_Temperatura_S01_S05_Batch.ipynb`; `resumen_u1_temperatura.json` |
| **Mijael · U2 (streaming)** | ¿Qué temperatura exterior se espera en Azángaro una hora después? | Temperatura en vivo; predicción +1 h; RMSE frente a persistencia; alerta ≤ 0 °C | Kafka (2 tópicos), Spark Structured Streaming (3 consultas), MLlib 4 algoritmos, evaluaciones de riesgo de helada | Cuaderno U2 de temperatura; `metricas_modelo_temperatura.csv`; Grafana fila 07 |
| **Común · Integración y DataOps** | ¿El sistema completo funciona junto y puede verificarse y repetirse? | Compuertas aprobadas, latencia del pipeline p50/p95, error de predicción en producción, manifiesto | Ejecución integrada con compuertas, Pushgateway/Prometheus, manifiesto JSON, auditoría de configuración | Cuaderno `U3_Integracion_DataOps_S13_S14.ipynb`; Grafana fila 08; [hardening](../hardening.md) |

Cada indicador se contrasta con una **línea base de persistencia** y los resultados se reportan **tal como salgan**. Los datos son modelados (Open-Meteo), parcialmente simulados o interpolados y llevan su etiqueta `origen` ([datos](../datos.md)).
