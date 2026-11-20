# Hardening y revisión técnica final

## Lista de comprobación aplicada (`scripts/auditoria_config.py`)
| Punto | Pregunta | Resultado |
|---|---|---|
| Versión de las imágenes | ¿Versión exacta, no `latest`? | Cumple |
| Reinicio | ¿Qué hace el contenedor si cae? | Cumple (`restart: unless-stopped`) |
| Salud | ¿Hay forma automática de saber si está **listo**? | Cumple (9 servicios permanentes) |
| Orden de arranque | ¿Espera a que su dependencia esté sana? | Cumple (`service_healthy`) |
| Secretos | ¿Hay credenciales escritas en el archivo? | Cumple (`${VARIABLE}`; `.env` ignorado) |
| Superficie expuesta | ¿Qué puertos se publican? | Cumple (11 puertos, todos en `127.0.0.1`) |
| Variables | ¿Están documentadas en `.env.example`? | Cumple |

## Bitácora de hallazgos y corrección
| # | Hallazgo | Corrección | Prueba de corrección |
|---|---|---|---|
| 1 | Ningún servicio declaraba si estaba listo; las dependencias esperaban solo a que arrancara | `healthcheck` + `service_healthy` | Auditoría «Salud» y «Orden» = Cumple; `up -d --wait` |
| 2 | Pushgateway aislado de Jupyter y sin `honor_labels` | Red de datos + `honor_labels: true` | Prometheus devuelve el valor recién publicado |
| 3 | Sin registro auditable de cada corrida integrada | Tabla `ejecuciones_integracion`, manifiesto, métricas y alertas | Dos corridas comparadas con `comparar()` |
| 4 | Variables de Mijael sin documentar | Agregadas a `.env.example` | Auditoría «Variables» = Cumple |
| 5 | **Predicciones desfasadas 5 h:** PySpark entrega los timestamps a Python sin zona horaria (hora local del contenedor, `TZ=America/Lima`) y el consumer los etiquetaba como UTC; la hora objetivo quedaba antes del propio evento y todo salía `es_retro = true`. El error en vivo del manifiesto del 17-nov comparaba horas distintas | Función `hora_peru()` en ambos consumers (fecha con zona −05:00), conexión PostgreSQL con `TimeZone=America/Lima`, PostgreSQL y Grafana en hora de Perú y `pyspark/sql/reparar_hora_peru.sql` (mide el desfase y solo corrige si es de 5 h) | `scripts/verificacion.sql`: desfase emisión−evento en segundos; objetivo = evento + h; `es_retro = f` en vivo; nueva ejecución integrada comparada con la anterior |
| 6 | El consumer de verificación rechazaba el tópico de temperatura (`choices` solo de humedad) y leía desde el offset 0 | Acepta los 4 tópicos, lee los últimos N mensajes y muestra la humedad del **suelo** como variable principal | `verificar_sistema.bat`, sección 4 |
| 7 | `.gitignore` excluía evidencias, resultados y modelos que la documentación presenta como verificables | Se versionan (pesan menos de 1 MB); siguen fuera `.env`, checkpoints, `bronze/` y `.spark-ivy/` | `git ls-files` en el repositorio |
| 8 | Tablero con tablas desbordadas y métricas de Spark de ambos integrantes mezcladas | Dashboard v4 en 3 partes (humedad → temperatura → común), tablas a ancho completo, Prometheus filtrado por consulta | `test_hardening` (paneles e ids únicos) y revisión visual |
| 9 | Logs con sufijos `-2min-1`/`-1` y ruido `py4j` que dificultaban la demo | `container_name` fijo y `py4j` en `WARNING` | Logs de la demo |

## Prueba de no regresión
Tras **cada cambio**: `python -m unittest discover -s pruebas -v` (27 pruebas) + `python scripts/auditoria_config.py` + **repetir la ejecución integrada** y comparar manifiestos. Cambia lo esperable (latencia, error del modelo: la fuente es en vivo); sería **regresión** que una compuerta pase de OK a FALLA o que el flujo procese cero filas.

## Riesgos aceptados
| Riesgo | Por qué se acepta | Qué cambiaría en producción |
|---|---|---|
| Kafka `PLAINTEXT`, 1 broker, sin autenticación | Laboratorio local; puertos en `127.0.0.1` | TLS + SASL, ≥ 3 brokers |
| Credenciales de laboratorio en `.env` y token de Jupyter simple | Equipo local; `.env` no versionado | Gestor de secretos y acceso autenticado |
| Sin healthcheck en `kafka-ui` y `kafka-exporter` | Imagen mínima; el exporter se observa desde Prometheus | Sondas desde el orquestador |
| Datos modelados, simulados e interpolados | No hay API gratuita con humedad del suelo observada cada 2 min | Sensores físicos al mismo contrato |
| Un nodo Spark por consumer | Volumen bajo | Clúster con checkpoints compartidos |
| Umbrales y costos didácticos | Demostran el flujo de decisión | Validación con agrónomo y tarifas reales |
