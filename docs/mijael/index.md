# Dimensión de Mijael Yurins Coaquira Justo · Temperatura exterior (Azángaro)

> **«¿Qué temperatura exterior se espera en la zona de referencia de Azángaro una hora después, a partir de los datos meteorológicos de Open-Meteo?»**

| | DimensiónU1 (batch) | DimensiónU2 (streaming) |
|---|---|---|
| Sesiones | S1–S5 | S6–S12 |
| Cuaderno | `pyspark/sesiones/U1_Batch_Temperatura/U1_Mijael_Temperatura_S01_S05_Batch.ipynb` | `pyspark/sesiones/Sensortemperatura/U2_Mijael_Temperatura_S06_S12_Tiempo_Real.ipynb` |
| Indicador | Perfil térmico diario, horas de helada y temperatura esperada +1 h (foto fija) | Temperatura en vivo y predicción +1 h con alerta de helada |
| Datos | Excel **simulado** `AgroSmart_Temperatura_U1.xlsx` | Carga inicial simulada (90 d) + API Open-Meteo real (≈60 d + tiempo real) |
| Salida | Tablas y gráficos del cuaderno | Fila 07 del Grafana común |

- [DimensiónU1](dimension-u1.md) · [DimensiónU2](dimension-u2.md)
- Coordenadas de la zona de referencia: **−14.91, −70.19** (configurables con `TEMP_LAT` / `TEMP_LON`).
- Infraestructura propia: tópicos `agrosmart-u2-temperatura-telemetria` y `…-empresarial`, tablas `*_temperatura`, modelo `modelos/temperatura_1h`, consumer `spark-consumer-temperatura`.
