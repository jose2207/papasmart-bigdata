# Mijael · DimensiónU1 — Temperatura histórica (batch, S1–S5)

**Indicador U1:** perfil térmico diario (mín/máx/media, horas bajo 0 °C) y **temperatura esperada a +1 h** por un modelo de regresión entrenado una vez sobre el histórico. Se reporta en el cuaderno.

| Sesión | Qué se hace | Evidencia |
|---|---|---|
| S1 | Clasificación batch/streaming, Lambda, ficha arquitectónica; calibración opcional contra la API real | Secciones 1.1–1.7 |
| S2 | Esquema explícito, lazy evaluation y `explain`, `withColumn`, resumen diario, ventana (media móvil, cambio horario), RDD, `cache` | 2.1–2.7 |
| S3 | −999, nulos y duplicados; **imputación con la fuente de respaldo** (marca `imputada`); Parquet por `anio_mes` | 3.1–3.5 |
| S4 | `lag/lead`, **división cronológica 80/20**, Lineal/Ridge/RF/GBT vs. persistencia, ablación hacia el conjunto desplegable en U2 | 4.1–4.4 |
| S5 | `resumen_u1_temperatura.json`, ficha U1 y checklist | Sección 5 |

**Diferencias respecto a la dimensión de José:** datos íntegramente simulados; imputación con respaldo en vez de descartar; división cronológica en el modelo U1 (la serie es temporal); objetivo a +1 h con lags.
**Verificación independiente:** Spark = pandas en conteos e imputaciones (esperado: 2880 filas, 30 códigos −999, 15 nulos, 25 duplicados del respaldo, 45 imputadas, 5 particiones `anio_mes`).
