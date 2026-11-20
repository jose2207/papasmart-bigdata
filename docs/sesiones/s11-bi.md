# S11 · BI/ML integrado en Grafana

**José · DimensiónU2.** Esta sesión aporta al monitoreo y predicción en tiempo real de la humedad.

El dashboard `AgroSmart Puno U2 — Humedad del suelo + aire | BI/ML y Observabilidad` está en `obs/grafana/dashboards/agrosmart_u2.json` y contiene 61 paneles organizados en 3 partes (Parte 1 humedad con predicción +1/+2/+3 h, Parte 2 temperatura con predicción +1 h y riesgo de helada, Parte 3 observabilidad, DataOps y costos): KPIs de telemetría y evaluación empresarial simulada; humedad suelo y aire; media por ventana; predicciones +1, +2, +3 h y comparación ML; validación de inferencias retrospectivas/prospectivas; estado de Spark y Prometheus; costos en soles y offsets Kafka.

**Condición para nivel A:** el docente debe visualizar en el mismo tablero, durante la sesión, datos del flujo empresarial, valores de humedad y las predicciones reales generadas por el modelo. Si el dashboard muestra únicamente capturas antiguas o un replay sin nuevos offsets, la demostración en vivo queda incompleta. Filtra `Last 90 days` para el histórico y cambia el rango para ver el modo continuo.
