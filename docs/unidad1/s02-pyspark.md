# S2 · Fundamentos PySpark

**José · DimensiónU1.** Aporte de esta sesión: lectura y transformación eficiente de la humedad.

1. Lectura con **esquema explícito** (`StructType`), no `inferSchema`.
2. **Lazy evaluation:** el plan se construye en milisegundos; la acción (`count`) ejecuta. Se mide ambos tiempos.
3. **`explain(True)`:** *predicate pushdown* y *column pruning* en el plan optimizado/físico.
4. `withColumn` con `to_timestamp`, `when/otherwise`, `lit`, `current_date`.
5. **Agrupaciones** (`groupBy().agg`) por categoría y por hora; **ventana** (`Window`) con media móvil de 3 h sin perder filas.
6. **RDD** `map` + `reduceByKey` (patrón MapReduce) y verificación cruzada con DataFrame; `cache()`.

**Advertencia de dominio:** la humedad es % volumétrico modelado, no mm ni sonda.
**Evidencia:** secciones 2.1–2.10 (capturas de `explain`, tablas y gráfico por hora).
