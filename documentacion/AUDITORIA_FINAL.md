# Auditoría de preparación — AgroSmart Puno (humedad + temperatura, U1–U3)

> **Actualizado el 19/11/2026.** Estado vigente: 27 pruebas, dashboard v4 en 3 partes (61 paneles), dos dimensiones (José: humedad · Mijael: temperatura) y flujo cada 2 min funcionando.

**Alcance:** solo humedad volumétrica de suelo 0–1 cm, humedad relativa del aire y eventos de evaluación empresarial simulada derivados de esas mismas lecturas. Este archivo no certifica que los servicios Docker estén ejecutándose en la computadora del usuario.

## Elementos desarrollados

- Organización acorde con el patrón del docente: `kafka/`, `pyspark/`, `obs/`, `docs/`, `uso-agrosmart/`, `overrides/` y `.github/workflows/`.
- Dos productores distinguibles: `producer_api_humedad.py` (API→Kafka) y `producer_evaluaciones.py` (telemetría Kafka→evaluación empresarial simulada Kafka).
- Consumidor Kafka de inspección por tópico y consumidor Spark persistente como proceso `spark-submit` separado de Jupyter.
- Contratos JSON Schema, fecha UTC, procedencia, valores en m³/m³ y %, validaciones y política de idempotencia.
- Structured Streaming de dos tópicos: ventanas de 1h, watermark de 2h, deduplicación y 3 checkpoints independientes.
- Entrenamiento Spark MLlib de 4 algoritmos y baseline para horizontes 1/2/3h; 12 comparaciones y 3 modelos elegidos solo por validación.
- Esquema PostgreSQL con tablas de telemetría, eventos empresariales, ventanas, predicciones, métricas ML, métricas streaming y costos.
- Exportador de métricas, Prometheus con reglas y dashboard de Grafana v4 en 3 partes (61 paneles: humedad, temperatura y operación común); 2 fuentes provisionadas.
- Costos mensuales **estimados en soles (S/)** a partir de supuestos explícitos y medidas de PostgreSQL cuando existan.
- MkDocs y publicación automatizable por GitHub Actions, matriz de rúbrica y bitácora de evidencia S6–S12.

## Comprobaciones realizadas sobre el código fuente

- **27 pruebas offline correctas** (originalmente 10) con `python -m unittest discover -s pruebas -v`: conversión, normalización, evento empresarial derivado, identificadores reproducibles, validación de límites, costos y presencia de la integración en el JSON de Grafana.
- Todos los scripts `.py` y celdas Python del notebook: sintaxis comprobada por `ast.parse`.
- Todos los archivos `.json`: parseo JSON.
- Todos los Compose, Prometheus, Grafana y MkDocs `.yml`: sintaxis YAML comprobada con PyYAML.
- Todas las entradas de navegación de `mkdocs.yml` apuntan a documentos existentes.

## Comprobaciones que no se pueden asegurar desde esta entrega

- `docker compose config -q`, descarga/build de imágenes y conectividad real entre contenedores: **no había Docker operativo en el entorno de creación**.
- Descarga real de Open-Meteo desde la red de tu equipo y descarga Maven del conector Spark Kafka.
- Entrenamiento MLlib completo sobre los datos actuales, consumo streaming, avance de watermark, recuperación, alertas Firing/Normal y paneles con datos reales.
- Publicación de un GitHub propio y URL pública de MkDocs; notas de sustentación del docente.

**Requisito S12:** tomar capturas y escribir **observado**, **fecha**, **consultas/offsets** y **salida SQL** en la bitácora de evidencias. No presentar una estimación o un ejemplo como una medición o resultado real.
