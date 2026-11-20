# Equipo y aporte individual

| Integrante | Dimensión | DimensiónU1 (batch) | DimensiónU2 (streaming) | Evidencia verificable |
|---|---|---|---|---|
| **Jose Armando Mamani Poccohuanca** | Humedad del suelo (Puno) | Excel real modelado + fallas inyectadas; calidad, Parquet, 5 modelos y ablación | Humedad en vivo; predicción +1, +2 y +3 h; consumer Spark propio; tablero filas 01–06 | Cuadernos, `metricas_modelo.csv`, commits |
| **Mijael Yurins Coaquira Justo** | Temperatura exterior (Azángaro) | Excel simulado; imputación con respaldo; lag/lead; modelo cronológico | Temperatura en vivo; predicción +1 h con alerta de helada; consumer Spark propio; tablero fila 07 | Cuadernos, `metricas_modelo_temperatura.csv`, commits |

**Común al grupo** (se presenta una sola vez; cada integrante responde sobre ello): arquitectura, DataOps, hardening, documentación, demo y repositorio ([DataOps](dataops.md), [hardening](hardening.md), [demo](demo.md)).

Cada integrante demuestra además **una decisión propia, con lo que gana y lo que cuesta** (láminas de la sustentación): José, *medir contra la persistencia y aceptar un resultado negativo*; Mijael, *entrenar con las variables que el streaming sí tiene (sin lags)*.
