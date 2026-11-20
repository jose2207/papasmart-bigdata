# Pregunta central, variable de interés y dimensiones del equipo

> Redacción propuesta siguiendo el brief oficial de lambda26 (sección 2 y 3). Si el docente fijó otra formulación, cámbiala aquí y en `brief.md` manteniendo la estructura: **1 pregunta central → 1 variable de interés → 1 dimensión por integrante, medida con un indicador U1 (batch) y uno U2 (streaming)**.

## Pregunta central del proyecto (hilo conductor único)
**¿Cómo anticipar a corto plazo las condiciones meteorológicas de riesgo agrícola del altiplano de Puno —estrés hídrico del suelo y heladas— a partir de datos de Open-Meteo?**

## Variable de interés
**Condiciones meteorológicas de riesgo agrícola en el altiplano de Puno.** Se dimensiona en sus componentes medibles: la **humedad del suelo** (estrés hídrico) y la **temperatura exterior** (heladas). Todas las dimensiones convergen en **un solo tablero de Grafana**.

## Dimensiones, indicadores e instrumentos
| Integrante | Dimensión | **DimensiónU1** · indicador batch (sin tiempo real) | **DimensiónU2** · indicador streaming (con tiempo real) | Fuente batch (U1) | Fuente streaming (U2) |
|---|---|---|---|---|---|
| **Jose Armando Mamani Poccohuanca** | **Humedad del suelo** (0–1 cm; humedad del aire como complemento) — *¿qué humedad del suelo se espera en Puno 1, 2 y 3 h después?* | Humedad histórica limpia (Parquet) y **humedad esperada** por un modelo de regresión sobre el histórico (foto fija) | Humedad en vivo y **predicción a +1, +2 y +3 h** actualizándose dato por dato | Excel `AgroSmart_Humedad_U1.xlsx` (real modelado + fallas inyectadas + 1 hoja simulada) | API Open-Meteo `soil_moisture_0_to_1cm` + `relative_humidity_2m` → Kafka |
| **Mijael Yurins Coaquira Justo** | **Temperatura exterior** — *¿qué temperatura exterior se espera en la zona de referencia de Azángaro una hora después, a partir de los datos meteorológicos de Open-Meteo?* | Temperatura mín./máx./media diaria y **horas de helada**; **temperatura esperada a +1 h** por regresión sobre el histórico (foto fija) | Temperatura en vivo y **predicción a +1 h** con **alerta de helada** | Excel `AgroSmart_Temperatura_U1.xlsx` (**simulado**) | API Open-Meteo `temperature_2m` → Kafka |

Cada integrante construye y defiende **sus dos capas** (batch y streaming); ambos usan el mismo patrón Lambda y la misma infraestructura (Kafka, Spark, PostgreSQL, Prometheus, Grafana) con tópicos, tablas, modelos y consumers **propios**.

## Cómo se combinan en el tablero final
Una sola historia: **riesgo agroclimático del altiplano = helada (temperatura, Mijael) + estrés hídrico (humedad del suelo, José)**. En Grafana: filas 01–06 de José y fila 07 de Mijael, en el mismo dashboard.
*Nota de coherencia:* la dimensión de José usa la zona de referencia de **Puno** (−15.84, −70.02) y la de Mijael **Azángaro** (−14.91, −70.19); las une la variable de interés (altiplano de Puno), no el mismo punto. Si el docente exige una sola zona, basta cambiar `AGRO_LAT/AGRO_LON` o `TEMP_LAT/TEMP_LON` en el `.env`.

## Criterio para dar por respondida la pregunta central
1. **DimensiónU1 (ambos):** histórico validado (conteos Spark = pandas), Parquet particionado y modelo batch comparado contra persistencia.
2. **DimensiónU2 (ambos):** flujo Kafka → Spark → PostgreSQL → Grafana funcionando, con 3 consultas por integrante, sin duplicados, observable (Prometheus) y con costos en S/.
3. **Predicción:** cada modelo se compara con la persistencia sobre **datos reales** y se reporta el resultado **tal como salga**, incluso si no la supera.
4. Se declaran las limitaciones (datos modelados o simulados, sin validación con sensores físicos).

## Resultados (completar tras ejecutar — no se inventan)
| Integrante | Indicador | Dónde se obtiene | Valor |
|---|---|---|---|
| José | Filas Bronze→Silver, −999, duplicados; mejor modelo U1 vs. baseline; ablación | `U1_Batch_Humedad/artifacts/resumen_u1.json` | 1 439 → 1 392 filas (47 descartadas), 25 errores −999, 30 duplicados; **Ridge** RMSE 0,90 pp, R² 0,974 frente a 5,59 pp de la línea base (promedio) |
| José | Ganador, RMSE/MAE/R² y persistencia en +1/+2/+3 h | `Sensorhumedad/resultados/metricas_modelo.csv` | Regresión lineal: RMSE 1,17 / 1,79 / 2,31 pp frente a 1,10 / 1,64 / 2,05 de la persistencia — **no la supera** (resultado negativo reportado) |
| Mijael | Filas, −999, imputadas con respaldo; mejor modelo U1 vs. persistencia | `U1_Batch_Temperatura/artifacts/resumen_u1_temperatura.json` | 2 880 filas, 30 errores −999, 45 imputadas con respaldo, 25 duplicados; **Lineal con lags** RMSE 0,92 °C frente a 1,50 °C de la persistencia |
| Mijael | Ganador, RMSE/MAE/R² y persistencia en +1 h | `Sensortemperatura/resultados/metricas_modelo_temperatura.csv` | **Árbol de decisión**: RMSE 1,14 °C, R² 0,946 frente a 1,63 °C de la persistencia (−30 %) |
| Ambos | Registros descargados de la API Open-Meteo | Cuadernos U2, sección 2.1b · tabla `api_descargas` · [Big Data histórico](../big-data-historico.md) | **131 767 por dimensión** (1 447 Forecast + 130 320 históricos ERA5), **263 534 en total** |
| Ambos | Conteos simulado / API / predicciones | `evidencias/evidencia_u2*.json` y `evidencias/verificacion_ultima.txt` | Ver [informe](../informe-proyecto.md), sección 10 |

**Conclusión:** la pregunta central se responde **parcialmente**. Para las **heladas**, el modelo de temperatura a +1 h supera a la persistencia (1,14 °C frente a 1,63 °C; −26 % en vivo y −46 % con el histórico) y la alerta ≤ 0 °C funciona en vivo. Para el **estrés hídrico**, la humedad del suelo cambia tan poco entre horas que repetir el último valor es más exacto que el modelo (1,17 frente a 1,10 pp a +1 h); el sistema la monitorea y la proyecta, pero no mejora a la persistencia. Los datos son modelados (Open-Meteo) y parcialmente simulados.

## Limitaciones
Open-Meteo es **estimación de modelo**, no sensor; la carga inicial es **simulada**; en U1 de José una hoja se deriva del objetivo y **todo el U1 de Mijael es simulado**; un solo nodo; el suelo cambia poco entre horas; umbrales (20 % de humedad, 0 °C de helada) y costos en S/ son **didácticos**; no se estiman dosis de riego ni alertas oficiales.
