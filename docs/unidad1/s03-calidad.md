# S3 · Calidad de datos y particionamiento

**José · DimensiónU1.** Aporte de esta sesión: calidad del dato y capa Gold particionada.

| Capa | Contenido |
|---|---|
| Bronze | CSV/Excel tal cual |
| Silver | Integrado (suelo + aire + suelo 1–3 cm), sin −999, sin nulos críticos ni duplicados |
| Gold | Parquet particionado por `anio_mes` |

Controles: **(1)** esquema obligatorio, **(2)** nulos *y* códigos de error (`isNull()` no detecta −999), **(3)** duplicados con `Window + row_number` (conserva la fila con menos nulos), **(4)** dominio 0–100 %.
**Verificaciones independientes:** conteos de Spark = conteos de pandas; filas esperadas en Silver = 1392; particiones `2026-09`, `2026-10`, `2026-11`; ida y vuelta de Parquet sin pérdidas; `PartitionFilters` en `explain`.
**Evidencia:** secciones 3.1–3.6.
