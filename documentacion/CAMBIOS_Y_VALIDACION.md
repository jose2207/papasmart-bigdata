# Cambios respecto a AgroSmart_Puno_U2_FINAL y validación

## Qué se agregó / cambió
- `pyspark/sesiones/U1_Batch_Humedad/`: cuaderno U1 (S1–S5), Excel + CSV de humedad y generador (`generar_datos_u1.py`).
- `pyspark/sesiones/Sensorhumedad/U2_AgroSmart_S06_S12_Humedad_Tiempo_Real.ipynb`: reemplaza al cuaderno anterior; ahora cubre S6–S12 en orden ejecutable, con monitor en vivo, Prometheus, costos, pronóstico a 3 h y evidencias.
- `uso-agrosmart/producer/simulador_humedad.py` (+3 pruebas): carga inicial simulada reproducible (`origen='simulado_carga_inicial'`).
- `obs/grafana/dashboards/agrosmart_u2.json`: ahora es el dashboard v2 aportado (33 paneles), rango por defecto 180 días.
- `uso-agrosmart/contratos/telemetria.json`: ejemplo solo con humedad (sin temperatura/precipitación).
- `pyspark/Dockerfile`: se agrega `openpyxl` (leer el Excel). Reconstruir con `--build`.
- Se excluyen checkpoints y modelos antiguos (se regeneran) y la caché Maven (se vuelve a descargar).

## Validado en el entorno de creación (sin Docker)
- `python -m unittest discover -s pruebas` → 13 pruebas OK (10 originales + 3 del simulador).
- Sintaxis (`ast.parse`) de todas las celdas de ambos cuadernos; JSON de cuadernos y dashboard; YAML de compose/prometheus/mkdocs.
- Los conteos de calidad de la U1 se verificaron con una réplica en pandas (1439 → 1392 filas en Silver; particiones 2026-09/10/11).

## NO validado aquí (debes confirmarlo en tu laptop)
- Ejecución real de PySpark/MLlib, Kafka, Spark Streaming, Prometheus y Grafana (no había Docker ni PySpark disponibles).
- Las métricas (RMSE/MAE/R²) dependerán de la corrida: no se inventaron resultados.
- Descarga de Open-Meteo y del conector Maven.


## Segunda dimensión: Mijael Yurins Coaquira Justo (temperatura exterior, Azángaro)
**Agregado:** cuadernos `U1_Mijael_Temperatura_S01_S05_Batch.ipynb` y `U2_Mijael_Temperatura_S06_S12_Tiempo_Real.ipynb`; Excel simulado de U1 y su generador; `open_meteo_temperatura.py`, `simulador_temperatura.py`, `producer_api_temperatura.py`, `decisiones_temperatura.py`, `producer_evaluaciones_temperatura.py`, `producer_tardio_temperatura.py`; `consumer_streaming_temperatura.py` + `start_consumer_temperatura.sh`; `schema_temperatura.sql`; servicios Compose con perfiles `*-temperatura`; métricas y alertas de temperatura en el exporter/Prometheus; fila 07 en el dashboard común (13 paneles); contratos JSON; 4 pruebas nuevas; documentación (pregunta central, brief oficial, páginas de Mijael).
**Se reorganizó la documentación** para seguir el brief oficial: 1 pregunta central → variable de interés → 1 dimensión por integrante con **DimensiónU1** (indicador batch) y **DimensiónU2** (indicador streaming).
**Se modificaron** (sin cambiar su comportamiento): `crear_topicos.py` (ahora crea 4 tópicos), `compose.yml` de uso-agrosmart y `compose.kafka.yml` (servicios nuevos), `pyspark/compose.yml` (monta el SQL de temperatura), exporter y alerts (métricas nuevas, opcionales), dashboard (paneles agregados).
**Validado sin Docker:** 17 pruebas unitarias; sintaxis de scripts y celdas; JSON/YAML; MkDocs build. **No validado aquí:** ejecución real de Spark/Kafka/Docker/Grafana, descarga de Open-Meteo y las métricas del modelo de temperatura. Las coordenadas de Azángaro (−14.91, −70.19) son aproximadas.

## Flujo cada 2 minutos
Agregado: `interpolacion_2min.py`, `producer_api_2min.py` (servicios `producer-humedad-2min` y `producer-temperatura-2min`, perfil `tiempo-real-2min`), parámetro `forecast_days` en los clientes de Open-Meteo, contratos con el nuevo `origen`, 3 pruebas, `iniciar_tiempo_real_2min.bat` y la página `docs/tiempo-real-2-minutos.md`. Validado sin Docker (20 pruebas); **no** validado contra la API real ni Kafka.

## Producto final (Unidad 3)
Agregado: healthchecks y `service_healthy` en Compose; `healthcheck_consumer.py`; `schema_integracion.sql`; métricas y alertas `agrosmart_int_*`; fila 08 de Grafana (DataOps); `scripts/auditoria_config.py`; `pruebas/test_hardening.py` (27 pruebas en total); CI (`.github/workflows/ci.yml`); cuaderno `U3_Integracion_DataOps_S13_S14.ipynb`; páginas de MkDocs según la plantilla mínima (instalación, uso, módulos, pruebas, equipo, repositorio, limitaciones, DataOps, hardening, demo, matriz de trazabilidad); presentación `presentacion/AgroSmart_Puno_U3_Producto_Final.pptx` (35 láminas, basada en el PPT de ejemplo). **No validado aquí:** ejecución real de Docker/Spark/Kafka/Grafana ni los valores de KPI y métricas (se completan con la corrida).
