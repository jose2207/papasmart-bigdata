# S1 · Arquitectura Big Data: Lambda y Kappa

**José · DimensiónU1.** Aporte de esta sesión: elige y justifica la arquitectura.

- **5V:** volumen modesto (1 lectura/h), variedad (Excel, CSV, JSON, eventos), velocidad horaria, veracidad limitada (valores modelados), valor (anticipar humedad).
- **Clasificación:** entrenar con histórico y limpiar → *batch*; recibir y predecir cada lectura → *streaming*; Grafana → *serving*.
- **Decisión:** **Lambda** (batch + speed + serving). Solo el **modelo entrenado** cruza del batch al speed layer; el riesgo es el *drift* si ambos calculan distinto (se mitiga con el mismo `PipelineModel`).

```
Open-Meteo / Excel ─► BATCH (PySpark+Parquet+MLlib) ─► modelo ─┐
                  └─► Kafka ─► SPEED (Structured Streaming) ───┴─► PostgreSQL ─► Grafana
```
**Evidencia:** secciones 1.1–1.6 del cuaderno U1 (entorno verificado, clasificación, ficha, reflexión).
