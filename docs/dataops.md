# DataOps / DevOps aplicado

| Práctica | Cómo se aplica | Verificación |
|---|---|---|
| **Comprobación de salud** | `healthcheck` en Kafka, PostgreSQL, Jupyter, exporter, Prometheus, Pushgateway, Grafana y los dos consumers Spark (heartbeat en `metricas_pipeline`) | `docker ps` → `(healthy)` |
| **Espera por dependencia** | `depends_on` con `condition: service_healthy` (Grafana→Prometheus→exporter, Kafka UI y exporter→Kafka, Jupyter y consumers→PostgreSQL); `up -d --wait` | `scripts/auditoria_config.py` |
| **Configuración fuera del código** | Todo por `${VARIABLE}` desde `.env` (no versionado) y `.env.example` documentado; puertos solo en `127.0.0.1` | Auditoría: «Secretos» y «Variables» |
| **Ejecución integrada con compuertas** | Cuaderno `U3_Integracion_DataOps_S13_S14.ipynb`: 10 compuertas previas, compuertas de calidad y plausibilidad, flujo en vivo, publicación y confirmación en Prometheus | Manifiesto + tablero (fila 08) |
| **Manifiesto de ejecución** | JSON con runId, versiones, **huellas SHA-256 de la configuración**, compuertas, KPI y duración; fila en `ejecuciones_integracion` | `evidencias/manifiesto_<runId>.json` |
| **CI** | GitHub Actions: pruebas, auditoría, `compose config` y `mkdocs --strict` | Pestaña Actions |

**KPI con percentiles:** latencia del pipeline = `fecha_ingesta − emitido_utc` sobre el flujo vivo (24 h). Se publican **p50** y **p95**; la compuerta de plausibilidad usa el **p50 (< 60 s)** y el p95 (> 300 s) es **advertencia**. Nunca solo el promedio.
