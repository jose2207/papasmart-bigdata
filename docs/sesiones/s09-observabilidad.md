# S9 · Prometheus, Grafana, alertas y costos en soles

**José · DimensiónU2.** Esta sesión aporta al monitoreo y predicción en tiempo real de la humedad.

### Monitoreo

Prometheus (`localhost:9095`) consulta cada 15 s `exporter:9200`, `kafka-exporter:9308`, Prometheus y Pushgateway. Las métricas de PostgreSQL incluyen contadores de eventos, predicciones, ventanas, estado/heartbeat y duración de las 3 consultas. El retraso de offsets se expone **solo si Spark lo devuelve** (no se inventa valor 0).

Alertas definidas en `obs/prometheus/alerts.yml`: exportador inaccesible, base inaccesible, consumer detenido, heartbeat antiguo, microlote lento (>10 s) y lag alto (>30 offsets). Los umbrales son de laboratorio, deben justificarse y demostrarse Normal→Firing→Normal. El dashboard usa Prometheus **y** PostgreSQL.

### Costos en S/

Ejecutar `pyspark/scripts/costos_pen.py`. El script usa los conteos y el tamaño aproximado por fila de PostgreSQL cuando está disponible, con escenarios de 1, 24 y 240 eventos/hora. **Tarifas didácticas:** S/0.30 por hora de cómputo y S/0.40 por GB-mes de almacenamiento, ambas editables. Los costos son **parciales, no cotización**; excluyen API comercial, red, electricidad, backups reales, impuestos y personal. Escalado: antes de aumentar recursos, medir MB/s, eventos/s, duración/trigger, lag, RAM y retención; solo entonces proponer particiones, workers y nuevos recursos.
