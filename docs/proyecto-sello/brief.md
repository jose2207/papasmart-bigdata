# Brief técnico-analítico — AgroSmart Puno (plantilla oficial lambda26, completada)

## 1. Datos del equipo
- **Nombre del equipo:** AgroSmart Puno · **Grupo:** 11 · **Sección:** GU · **Curso:** Big Data (2026-2, Juliaca)
- **Repositorio (URL):** [https://github.com/jose2207/papasmart-bigdata](https://github.com/jose2207/papasmart-bigdata) · **Documentación publicada:** [https://jose2207.github.io/papasmart-bigdata/](https://jose2207.github.io/papasmart-bigdata/)
- **Topics del repositorio configurados:** sí — `campus-juliaca`, `semestre-2026-2`, `linea-cdia`, `tipo-ps`, `bigdata`, `seccion-gu`, `grupo-11-agrosmart-puno`, `apache-kafka`, `spark-streaming`, `pyspark`, `grafana`, `prometheus`, `open-meteo`
- **Integrantes:**

| Integrante | Rol o énfasis previsto |
|---|---|
| Jose Armando Mamani Poccohuanca | Humedad del suelo; énfasis en batch/Spark y BI/ML |
| Mijael Yurins Coaquira Justo | Temperatura exterior; énfasis en streaming/Kafka y observabilidad |

(Énfasis de coordinación; cada integrante construye de extremo a extremo su dimensión con sus indicadores U1 y U2.)

## 2. Dominio del proyecto
- **Nombre:** AgroSmart Puno — riesgo agroclimático del altiplano.
- **Problema (2–4 líneas):** en el altiplano de Puno las **heladas** y el **estrés hídrico del suelo** afectan los cultivos. Se necesita observar en continuo la temperatura y la humedad del suelo y anticipar su valor en las horas siguientes para apoyar la vigilancia agroclimática.
- **Dominio de datos:** agroclimatología / IoT-meteorología; se mide temperatura a 2 m y humedad volumétrica del suelo 0–1 cm (y humedad relativa del aire).
- **Variable de interés:** condiciones meteorológicas de riesgo agrícola en el altiplano de Puno.
- **Pregunta central:** ¿cómo anticipar a corto plazo las condiciones meteorológicas de riesgo agrícola del altiplano de Puno —estrés hídrico del suelo y heladas— a partir de datos de Open-Meteo?
- **Usuarios / actores:** técnico agrícola o gestor de riego/vigilancia (lee el tablero), y el sistema de alertas didáctico.
- **Arquitectura prevista:** **Lambda**, porque se necesita histórico (descripción y entrenamiento) **y** tiempo real (inferencia y alerta); el modelo entrenado en batch se despliega en streaming (criterio S1, 2.5.1).
- **Fuente batch:** Excel/CSV por integrante (`AgroSmart_Humedad_U1.xlsx`: Open-Meteo real modelado + fallas inyectadas + hoja simulada; `AgroSmart_Temperatura_U1.xlsx`: simulado calibrado al clima del altiplano). Es un dataset realista, **no** medición de sensores físicos.
- **Fuente de eventos en tiempo real:** API Open-Meteo (modelada), publicada a Kafka como evento horario; **carga inicial simulada** previa de 90 días por integrante.
- **¿Misma fuente en batch y streaming?** Sí en espíritu: el mismo origen (Open-Meteo) visto como lectura en vivo (U2) y como acumulación histórica (U1).
- **¿Continúa un proyecto anterior?** Continúa el proyecto AgroSmart Puno U2 del propio equipo.

## 3. Dimensiones de análisis y fuentes previstas
Tabla de asignación (detalle en [pregunta central y dimensiones](pregunta-general.md)):

| Integrante | Dimensión | Indicador U1 (batch) | Indicador U2 (streaming) | Fuente batch | Fuente streaming |
|---|---|---|---|---|---|
| Jose A. Mamani P. | Humedad del suelo | Humedad histórica y humedad esperada (regresión, foto fija) | Humedad en vivo y predicción +1/+2/+3 h | Excel humedad | API `soil_moisture_0_to_1cm` → Kafka |
| Mijael Y. Coaquira J. | Temperatura exterior (Azángaro) | Mín/máx/media diaria, horas de helada y temperatura esperada +1 h | Temperatura en vivo y predicción +1 h con alerta de helada | Excel temperatura | API `temperature_2m` → Kafka |

### Dimensión: Humedad del suelo (integrante: Jose Armando Mamani Poccohuanca)
- **Relación con la pregunta central:** componente *estrés hídrico* del riesgo agroclimático.
- **Decisión que habilita:** priorizar la revisión de parcelas cuando la humedad esperada baje de un umbral didáctico (20 %).
- **Indicador U1:** ¿cuánta humedad del suelo explican aire y hora, y qué humedad cabe esperar? Métrica: RMSE/MAE/R² frente a baseline; humedad esperada por el modelo.
- **Modelo U1:** regresión (Lineal, Ridge, Elastic Net, RF, GBT), una sola vez; ablación sin la variable simulada.
- **Fuente batch:** Excel (hojas `suelo_0_1cm`, `aire_2m`, `suelo_1_3cm_sim`; clave `fecha_hora`).
- **Salida U1:** cuaderno `U1_AgroSmart_S01_S05_Humedad_Batch.ipynb`.
- **Indicador U2:** humedad del suelo en vivo y su valor a +1, +2 y +3 h.
- **Modelo U2:** series de tiempo (4 algoritmos × 3 horizontes) comparado con persistencia, corriendo en Spark Structured Streaming.
- **Fuente streaming:** tópico `agrosmart-u2-humedad-telemetria` (evento_id, fecha_evento, ubicacion, humedad_suelo_m3m3, humedad_suelo_pct, humedad_aire_pct, origen).
- **Salida U2:** filas 01–06 del Grafana común.
- **Se combina con:** la temperatura (Mijael) en el mismo tablero.
- **Requisitos:** 1) El sistema debe ingerir humedad horaria en Kafka con contrato e idempotencia. 2) El sistema debe procesarla en streaming con ventanas, watermark y checkpoint sin duplicar. 3) El sistema debe predecir +1/+2/+3 h y compararlo con la persistencia.

### Dimensión: Temperatura exterior (integrante: Mijael Yurins Coaquira Justo)
- **Pregunta de la dimensión:** ¿qué temperatura exterior se espera en la zona de referencia de Azángaro una hora después, a partir de los datos meteorológicos de Open-Meteo?
- **Relación con la pregunta central:** componente *heladas* del riesgo agroclimático.
- **Decisión que habilita:** activar medidas de protección o vigilancia cuando la temperatura prevista cruza 0 °C (umbral didáctico).
- **Indicador U1:** perfil térmico (mín/máx/media diaria, horas bajo 0 °C) y temperatura esperada a +1 h. Métrica: °C y horas de helada; RMSE/MAE/R² frente a persistencia.
- **Modelo U1:** regresión con lags y hora (Lineal, Ridge, RF, GBT), división cronológica, una sola vez; ablación hacia el conjunto desplegable en U2.
- **Fuente batch:** Excel simulado (hojas `temperatura_2m`, `temperatura_respaldo`; clave `fecha_hora`); fallas −999, nulos y duplicados; imputación con el respaldo.
- **Salida U1:** cuaderno `U1_Mijael_Temperatura_S01_S05_Batch.ipynb`.
- **Indicador U2:** temperatura en vivo y proyectada a +1 h, con alerta si cruza ≤ 0 °C.
- **Modelo U2:** series de tiempo (4 algoritmos) frente a persistencia, en Spark Structured Streaming.
- **Fuente streaming:** tópico `agrosmart-u2-temperatura-telemetria` (evento_id, fecha_evento, ubicacion, temperatura_c, origen).
- **Salida U2:** fila 07 del Grafana común.
- **Se combina con:** la humedad del suelo (José) en el mismo tablero.
- **Requisitos:** 1) El sistema debe ingerir temperatura horaria desde Open-Meteo a Kafka. 2) El sistema debe derivar y guardar evaluaciones de riesgo de helada. 3) El sistema debe predecir la temperatura a +1 h en vivo y mostrar la alerta en Grafana.

**Qué SÍ cubre el proyecto:** temperatura y humedad del suelo del altiplano de Puno, Lambda con Kafka/Spark/PostgreSQL/Grafana/Prometheus, predicción a corto plazo, observabilidad y costos en S/.
**Qué NO cubre:** otras variables (lluvia, viento, radiación), sensores físicos, dosis de riego, alertas oficiales, alta disponibilidad, despliegue en nube.
**Unidad 3 (cerrada):** infraestructura compartida (Kafka, Spark, PostgreSQL, Prometheus, Grafana), ejecución integrada con compuertas y manifiesto (S13), hardening y prueba de no regresión (S14). Ver [informe del proyecto](../informe-proyecto.md).

## 4. Aprobación
Docente: ______ · Fecha: ______
