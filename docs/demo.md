# Demo end-to-end reproducible (10 minutos)

| Min. | Qué muestras | Comando o URL | Qué debe verse | Plan alternativo |
|---|---|---|---|---|
| 0–1 | Entorno sano | `docker ps` | Servicios `(healthy)` | Captura con fecha y hora |
| 1–2 | Compuertas previas | Cuaderno U3, sección 1 | 10 × OK | Manifiesto anterior |
| 2–4 | Flujo cada 2 min de ambos | `logs -f producer-humedad-2min producer-temperatura-2min` y Kafka UI | Offsets creciendo | Salida guardada |
| 4–5 | Batch: KPI p50/p95 y Gold | Cuaderno U3, sección 2 | p50 frente a p95 | Captura de 2.1 |
| 5–7 | Streaming, predicción y error en producción | Sección 3 y Grafana filas 01–08 | Filas nuevas y error | Captura del tablero |
| 7–8 | Prometheus confirma lo publicado | Sección 4 | devuelto = publicado | Consulta en `:9095` |
| 8–9 | Manifiestos de dos corridas | Sección 5 | Tabla esperable / regresión | JSON abierto |
| 9–10 | Hardening | `python scripts/auditoria_config.py` | Todos «Cumple/Aceptado» | Salida guardada |

**Antes de empezar:** verifica que los productores estén publicando (los offsets crecen). Toda captura de respaldo debe tener fecha y hora visibles. Otra persona puede repetir la demo siguiendo la [guía de ejecución](guia-ejecucion.md).
