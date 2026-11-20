# GUÍA DE EJECUCIÓN EN CMD — AgroSmart Puno (José: humedad · Mijael: temperatura · U1 + U2)

Todo se ejecuta en **CMD de Windows** (o PowerShell) **desde la raíz de esta carpeta** (donde está `.env`).
Requisito: Docker Desktop abierto ("Engine running"), internet (Open-Meteo y descarga del conector Spark-Kafka).

## 0. Antes de empezar (una sola vez)
1. Descomprime el ZIP, por ejemplo en `D:\C9\Big Data\AgroSmart_Puno_BigData_COMPLETO`.
2. **Usa las MISMAS claves de tu proyecto anterior.** Abre `.env` (notepad .env) y copia ahí `POSTGRES_PASSWORD`, `GRAFANA_ADMIN_PASSWORD` y `JUPYTER_TOKEN` que ya usabas.
   > Si cambias `POSTGRES_PASSWORD`, la base que ya existe en el volumen de Docker **rechazará** la conexión. Si es un proyecto nuevo, pon cualquier clave.
3. Verifica Docker:
```bat
cd /d "D:\C9\Big Data\AgroSmart_Puno_BigData_COMPLETO"
docker compose version
docker info
docker compose --env-file .env -f kafka/compose.yml config -q
docker compose --env-file .env -f pyspark/compose.yml -f pyspark/compose.kafka.yml config -q
```
(`config -q` no imprime nada si todo está bien.) Si el proyecto anterior ocupa los mismos puertos: `docker compose stop` **desde su carpeta** (no uses `down -v`).

## 1. UNIDAD 1 (batch) — solo Jupyter
```bat
docker compose --env-file .env -f pyspark/compose.yml -f pyspark/compose.kafka.yml up -d --build postgres jupyter
```
* Jupyter: http://localhost:4489/lab (token = `JUPYTER_TOKEN`)  ·  Spark UI: http://localhost:4041 (aparece al crear la SparkSession)
* Abre `U1_Batch_Humedad/U1_AgroSmart_S01_S05_Humedad_Batch.ipynb` y ejecuta **de arriba a abajo** (S1→S5).
* Los datos (Excel + CSV) ya están en `U1_Batch_Humedad/data/`. Para regenerarlos: `python generar_datos_u1.py` (opcional).

## 2. UNIDAD 2 (tiempo real) — orden estricto
**Paso 1 — Kafka (+ Kafka UI y exporter)**
```bat
docker compose --env-file .env -f kafka/compose.yml up -d
docker compose --env-file .env -f kafka/compose.yml ps
```
Kafka UI: http://localhost:48086

**Paso 2 — Crear los 2 tópicos**
```bat
docker compose --env-file .env -f uso-agrosmart/compose.yml --profile herramientas run --rm inicializar-topicos
```

**Paso 3 — Abre el cuaderno U2** `Sensorhumedad/U2_AgroSmart_S06_S12_Humedad_Tiempo_Real.ipynb` y ejecuta:
sección 0 → **Sesión 06** → **Sesión 07** (API + **carga inicial simulada**) → **sección 10.1** (entrenar modelos 1/2/3 h; solo la primera vez, antes de arrancar el consumer).
> El consumer de Spark **no arranca si faltan los modelos** (`modelos/humedad_1h|2h|3h`): por eso se entrena antes.

**Paso 4 — Streaming (S6 + S8 + tiempo real)**
```bat
docker compose --env-file .env -f pyspark/compose.yml -f pyspark/compose.kafka.yml --profile streaming up -d spark-consumer
docker compose --env-file .env -f uso-agrosmart/compose.yml --profile flujo up -d producer-evaluaciones
docker compose --env-file .env -f uso-agrosmart/compose.yml --profile replay run --rm producer-api-replay
docker compose --env-file .env -f uso-agrosmart/compose.yml --profile continuo up -d producer-api-continuo
```
* La primera vez `spark-consumer` descarga el conector de Maven: espera unos minutos.
* Debe iniciar **3 consultas**: `telemetria`, `empresarial`, `ventanas`.

**Paso 5 — Observabilidad y Grafana (S9/S11)**
```bat
docker compose --env-file .env -f obs/compose.yml up -d --build
```
| Qué | URL |
|---|---|
| Grafana (dashboard v4, 3 partes, 61 paneles) | http://localhost:3300 → Dashboards → AgroSmart U2 → rango por defecto **últimas 24 h + 4 h de pronóstico** (cámbialo a 7 o 90 días para ver la historia) |
| Prometheus Targets | http://localhost:9095/targets |
| Exportador PostgreSQL | http://localhost:9202/metrics |
| Exportador Kafka | http://localhost:49309/metrics |
| Kafka UI | http://localhost:48086 |
| MkDocs (opcional) | http://localhost:8008 |

Continúa en el cuaderno en orden: **Sesión 08** (consumer y **monitor en tiempo real 8.3**), **Sesión 09**, **Sesión 10** (entrenamiento e inferencia a 3 h), **Sesión 11** y (Mijael) **Sesión 12**.


## 2-bis. DIMENSIÓN DE MIJAEL (temperatura, Azángaro) — mismo Docker, tópicos y tablas propias
Requisitos: Kafka y Jupyter arriba (secciones 1 y 2, pasos 1–2; `inicializar-topicos` ya crea los 4 tópicos).

**DimensiónU1 (batch):** en Jupyter abre `U1_Batch_Temperatura/U1_Mijael_Temperatura_S01_S05_Batch.ipynb` y ejecútalo de arriba a abajo. Datos simulados en `U1_Batch_Temperatura/data/AgroSmart_Temperatura_U1.xlsx` (regenerar: `python generar_datos_u1_temperatura.py`).

**DimensiónU2 (streaming), orden estricto:**
1. Cuaderno `Sensortemperatura/U2_Mijael_Temperatura_S06_S12_Tiempo_Real.ipynb`: Paso 0 → 1 → **2** (API + carga inicial) → **3** (entrenar +1 h).
2. Streaming:
```bat
docker compose --env-file .env -f pyspark/compose.yml -f pyspark/compose.kafka.yml --profile streaming-temperatura up -d spark-consumer-temperatura
docker compose --env-file .env -f uso-agrosmart/compose.yml --profile flujo-temperatura up -d producer-evaluaciones-temperatura
docker compose --env-file .env -f uso-agrosmart/compose.yml --profile replay-temperatura run --rm producer-temp-replay
docker compose --env-file .env -f uso-agrosmart/compose.yml --profile continuo-temperatura up -d producer-temp-continuo
```
3. Grafana común (http://localhost:3300): fila **«07 · MIJAEL · TEMPERATURA»**, rango *Last 180 days*.
4. Verificar llegada de datos:
```bat
docker compose --env-file .env -f pyspark/compose.yml -f pyspark/compose.kafka.yml logs -f spark-consumer-temperatura
docker compose --env-file .env -f uso-agrosmart/compose.yml logs -f producer-temp-continuo
docker compose --env-file .env -f uso-agrosmart/compose.yml --profile verificacion-temperatura run --rm consumer-verificacion-temp
docker compose --env-file .env -f uso-agrosmart/compose.yml --profile verificacion-temperatura run --rm consumer-verificacion-empresa-temp
docker compose --env-file .env -f pyspark/compose.yml exec postgres psql -U agrosmart -d agrosmart_u2 -c "SELECT origen, COUNT(*), MAX(fecha_evento) FROM eventos_temperatura GROUP BY origen;"
docker compose --env-file .env -f pyspark/compose.yml exec postgres psql -U agrosmart -d agrosmart_u2 -c "SELECT estado, COUNT(*) FROM eventos_empresariales_temperatura GROUP BY estado;"
```
5. Pruebas S8: evento tardío `--profile pruebas-temperatura run --rm producer-evento-tardio-temperatura` (en `uso-agrosmart/compose.yml`) y reinicio del consumer con `stop` / `up -d spark-consumer-temperatura`.

> **RAM:** dos consumers Spark (humedad y temperatura) más Jupyter exigen memoria. Si Docker Desktop va justo (menos de ~8 GB), detén uno mientras demuestras el otro: `docker compose --env-file .env -f pyspark/compose.yml -f pyspark/compose.kafka.yml stop spark-consumer` (o `spark-consumer-temperatura`).
> Atajo: `iniciar_streaming_mijael.bat`.

## 2-ter. DATOS CADA 2 MINUTOS (José y Mijael a la vez)
Open-Meteo solo entrega estimaciones **horarias** de modelo (y la humedad del suelo no existe a menor resolución); no hay una API pública gratuita con humedad del suelo observada cada 2 min para Puno/Azángaro. El productor de 2 minutos consulta Open-Meteo (caché de 10 min) e **interpola linealmente entre las dos horas que rodean cada instante**; cada evento queda marcado `origen = open_meteo_interpolado_2min` (**no es un sensor**).
```bat
:: (con Kafka, los consumers de Spark y los modelos ya entrenados)
docker compose --env-file .env -f uso-agrosmart/compose.yml --profile tiempo-real-2min up -d producer-humedad-2min producer-temperatura-2min
docker compose --env-file .env -f uso-agrosmart/compose.yml logs -f producer-humedad-2min producer-temperatura-2min
:: detener
docker compose --env-file .env -f uso-agrosmart/compose.yml --profile tiempo-real-2min stop
```
Usa estos servicios **en lugar de** `producer-api-continuo` y `producer-temp-continuo`. Atajo: `iniciar_tiempo_real_2min.bat`. Para datos realmente observados cada 2 min haría falta un sensor físico (p. ej. ESP32 + sensor capacitivo de suelo y DS18B20) publicando a Kafka.

## 3. CÓMO VER LLEGAR LOS DATOS DE JOSÉ (en CMD)
```bat
:: Logs en vivo (Ctrl+C para salir, no detiene el contenedor)
docker compose --env-file .env -f pyspark/compose.yml -f pyspark/compose.kafka.yml logs -f spark-consumer
docker compose --env-file .env -f uso-agrosmart/compose.yml logs -f producer-api-continuo
docker compose --env-file .env -f uso-agrosmart/compose.yml logs --tail=40 producer-evaluaciones

:: Mensajes crudos en Kafka (5 de cada tópico)
docker compose --env-file .env -f uso-agrosmart/compose.yml --profile verificacion run --rm consumer-verificacion
docker compose --env-file .env -f uso-agrosmart/compose.yml --profile verificacion run --rm consumer-verificacion-empresa

:: Conteos en PostgreSQL
docker compose --env-file .env -f pyspark/compose.yml exec postgres psql -U agrosmart -d agrosmart_u2 -c "SELECT origen, COUNT(*), MAX(fecha_evento) FROM eventos_telemetria GROUP BY origen;"
docker compose --env-file .env -f pyspark/compose.yml exec postgres psql -U agrosmart -d agrosmart_u2 -c "SELECT horizonte_h, COUNT(*), SUM(CASE WHEN es_retro THEN 1 ELSE 0 END) retro FROM predicciones_humedad GROUP BY 1 ORDER BY 1;"

:: Estado de contenedores y recursos
docker ps
docker stats --no-stream
```
En el cuaderno (U2, Sesión 08, sección **8.3**) hay un **monitor en tiempo real**: cada evento de Kafka con su offset y la predicción que guardó Spark.

## 4. Pruebas S8 (opcionales, para sustentar)
```bat
:: Evento tardío (watermark)
docker compose --env-file .env -f uso-agrosmart/compose.yml --profile pruebas run --rm producer-evento-tardio
:: Checkpoint: reiniciar el consumer sin duplicados
docker compose --env-file .env -f pyspark/compose.yml -f pyspark/compose.kafka.yml stop spark-consumer
docker compose --env-file .env -f pyspark/compose.yml -f pyspark/compose.kafka.yml --profile streaming up -d spark-consumer
:: Pruebas unitarias sin Docker (necesita Python)
python -m unittest discover -s pruebas -v
```

## 5. Apagar sin perder evidencias
```bat
docker compose --env-file .env -f uso-agrosmart/compose.yml --profile flujo --profile continuo --profile flujo-temperatura --profile continuo-temperatura --profile tiempo-real-2min stop
docker compose --env-file .env -f obs/compose.yml stop
docker compose --env-file .env -f pyspark/compose.yml -f pyspark/compose.kafka.yml --profile streaming --profile streaming-temperatura stop
docker compose --env-file .env -f kafka/compose.yml stop
```
**Nunca uses `down -v`** si quieres conservar PostgreSQL, Kafka y Grafana. Atajos: `iniciar_base.bat`, `iniciar_streaming.bat` (José), `iniciar_streaming_mijael.bat`, `iniciar_tiempo_real_2min.bat`, `detener_todo.bat`.

## 6. Problemas frecuentes
| Síntoma | Causa / solución |
|---|---|
| `password authentication failed` | La clave del `.env` no coincide con la del volumen existente de PostgreSQL. Usa la clave anterior. |
| `network agrosmart-jose-kafka-net ... not found` | Primero levanta Kafka (Paso 1). |
| `ClassNotFoundException KafkaSourceProvider` / error Maven | Falta internet al descargar el conector; reintenta `up -d spark-consumer`. |
| `spark-consumer` se detiene: *falta modelos* | Ejecuta la sección 10.1 (Sesión 10) del cuaderno U2 (José: `modelos/humedad_*`; Mijael: `modelos/temperatura_1h`) primero. |
| Faltan tablas `*_temperatura` en una base ya existente | Ejecuta el Paso 0 del cuaderno U2 de Mijael o reinicia `spark-consumer-temperatura` (ambos aplican `schema_temperatura.sql`). |
| Puerto ocupado | Detén el proyecto anterior con `docker compose stop` en su carpeta. |
| Grafana vacío | Rango **Last 180 days**; confirma datasource PostgreSQL y que hay filas (sección 3). |
| No llegan eventos nuevos | La API entrega 1 dato por hora y el productor evita repetidos: no es una caída de Kafka. |
