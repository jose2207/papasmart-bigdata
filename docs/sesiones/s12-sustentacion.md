# S12 · Sustentación y demo ejecutiva

**José · DimensiónU2.** Esta sesión aporta al monitoreo y predicción en tiempo real de la humedad.

**Pitch de apertura (propuesta, 45–60 s):**

> Mi dimensión U2 de AgroSmart Puno es la predicción de humedad del suelo. Tomamos dos variables modeladas de Open-Meteo, publicamos telemetría y evaluaciones empresariales simuladas en Kafka y las procesamos con un consumidor Spark persistente. Comparamos cuatro algoritmos de MLlib en tres horizontes con métricas temporales, y mostramos KPIs y predicciones junto a Prometheus y Grafana. Esta es una validación académica, no una medición física del suelo.

**Demo técnica:** API → Producer Kafka (offset) → Consumer de prueba → Spark (3 consultas, watermark y checkpoint) → PostgreSQL → Prometheus → Grafana → costos S/ → GitHub/MkDocs. La etapa U1 y la parte U2 deberán presentarse con evidencia real del estudiante, no inventada.

**Seis subaspectos:** aporte individual, comunicación/orden, presentación personal/actitud, repositorio/estándares, MkDocs publicado y pitch/demostración. Ver [rúbrica](../proyecto-sello/u2-producto.md) y [bitácora de evidencias](../proyecto-sello/u2-evidencias.md).
