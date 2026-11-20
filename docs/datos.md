# Datos: qué es real, qué es simulado y qué es inyectado

| Conjunto | Contenido | Naturaleza | `origen` / etiqueta |
|---|---|---|---|
| `AgroSmart_Humedad_U1.xlsx` · `suelo_0_1cm` | Humedad suelo 0–1 cm, 1439 h | **Real modelado** (Open-Meteo) + **fallas inyectadas** (−999, nulos) | — |
| · `aire_2m` | Humedad aire, 1469 filas | Real modelado + nulos + **30 duplicados inyectados** | — |
| · `suelo_1_3cm_sim` | Suelo 1–3 cm | **Simulado** a partir del objetivo | — |
| `simulado_carga_inicial.csv` | 90 días horarios antes del histórico API | **Simulado** (`simulador_humedad.py`, semilla 42) | `simulado_carga_inicial` |
| `historico_open_meteo.csv` | ≈60 días horarios | **Real modelado** | `open_meteo_modelado` |
| Tiempo real | Interpolación cada 2 min de las estimaciones horarias | **Real modelado interpolado** | `open_meteo_interpolado_2min` |
| Histórico Open-Meteo (Archive API, ERA5) | 2012–2026 por hora: suelo 0–7 cm y aire 2 m · **130 320 h** | **Real (reanálisis)** · ver [Big Data histórico](big-data-historico.md) | `open_meteo_archive_era5` |

## Reglas de calidad (U1)
1. `−999` es código de error: se **descarta** la fila (no se imputa).
2. Nulo en el **objetivo**: se descarta. Nulo en **aire**: se descarta para el modelo.
3. Duplicados por `fecha_hora`: se conserva la fila con **menos nulos** (`Window + row_number`).
4. Control de dominio: humedad entre 0 y 100 %.

## Reglas de continuidad (U2)
- La simulación termina **1 h antes** del primer dato de la API (sin huecos ni solapes).
- División cronológica 70/15/15 con brecha de *h* filas; **el 15 % final es API real**.
- `es_retro = TRUE` marca predicciones cuyo objetivo ya ocurrió (replay); no se mezclan con las prospectivas al evaluar.


## Dimensión de Mijael (temperatura, Azángaro)
| Conjunto | Contenido | Naturaleza | `origen` |
|---|---|---|---|
| `AgroSmart_Temperatura_U1.xlsx` · `temperatura_2m` | 2880 h (120 días) | **Simulado** (`simulador_temperatura.py`, semilla 11) + **−999 (30) y nulos (15) inyectados** | — |
| · `temperatura_respaldo` | 2905 filas | **Simulado** (sesgo +0.4 °C) + nulos + **25 duplicados** | — |
| `simulado_carga_inicial_temp.csv` | 90 días antes del histórico API | **Simulado** (semilla 7) | `simulado_carga_inicial` |
| `historico_open_meteo_temp.csv` y tiempo real | ≈60 días + interpolación cada 2 min | **Real modelado** (`temperature_2m`) | `open_meteo_modelado` / `open_meteo_interpolado_2min` |
| Histórico Open-Meteo (Archive API, ERA5) | 2012–2026 por hora: `temperature_2m` · **130 320 h** | **Real (reanálisis)** · ver [Big Data histórico](big-data-historico.md) | `open_meteo_archive_era5` |

Reglas U1: −999 y nulos se tratan como faltantes y se **imputan con el respaldo** (`imputada=true`); si ninguna fuente tiene dato, se descarta. Reglas U2: la simulación termina 1 h antes del primer dato de la API; prueba = último 15 % (API real).

## Flujo cada 2 minutos (ambas dimensiones)
| Conjunto | Contenido | Naturaleza | `origen` |
|---|---|---|---|
| Tiempo real cada 2 min | 1 evento cada 2 min por dimensión | **Interpolación lineal** de estimaciones horarias reales de Open-Meteo (no es sensor) | `open_meteo_interpolado_2min` |

Ver [flujo cada 2 minutos](tiempo-real-2-minutos.md).
