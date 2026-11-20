# AgroSmart Puno · Proyecto final Big Data — Unidades 1, 2 y 3 · José (humedad del suelo) y Mijael (temperatura)

**Grupo 11 · Sección GU · Big Data · Universidad Peruana Unión, Juliaca · 2026-2**
**Documentación publicada (MkDocs):** https://jose2207.github.io/papasmart-bigdata/ · **Informe del proyecto (14 secciones):** [`docs/informe-proyecto.md`](docs/informe-proyecto.md)

| Entregable U3 | Dónde |
|---|---|
| Presentación (31 láminas), guion de exposición e informe del proyecto en PDF | `presentacion/AgroSmart_Puno_U3_Producto_Final.pptx` · `presentacion/Guion_de_exposicion_AgroSmart_Puno_U3.pdf` · `presentacion/Informe_del_proyecto_AgroSmart_Puno_U3.pdf` |
| Ejecución integrada (compuertas + manifiesto) | `pyspark/sesiones/U3_Integracion/U3_Integracion_DataOps_S13_S14.ipynb` · `…/evidencias/manifiesto_20261120T060237Z.json` (24/24) |
| Verificación de todo el sistema en un archivo | `verificar_sistema.bat` → `evidencias/verificacion_ultima.txt` |
| Hardening, auditoría y pruebas | `docs/hardening.md` · `scripts/auditoria_config.py` · `python -m unittest discover -s pruebas` (27) · CI en `.github/workflows/` |
| Corrección de hora de Perú (caso de error) | `aplicar_hora_peru.bat` · `pyspark/sql/reparar_hora_peru.sql` |

> **EMPIEZA AQUÍ:** `GUIA_EJECUCION_CMD.md` (todos los comandos de CMD, en orden) y los dos cuadernos:
> **José (humedad del suelo)**
> * **DimensiónU1 (S1–S5, batch):** `pyspark/sesiones/U1_Batch_Humedad/U1_AgroSmart_S01_S05_Humedad_Batch.ipynb` (datos en Excel: `U1_Batch_Humedad/data/AgroSmart_Humedad_U1.xlsx`)
> * **DimensiónU2 (S6–S12, tiempo real):** `pyspark/sesiones/Sensorhumedad/U2_AgroSmart_S06_S12_Humedad_Tiempo_Real.ipynb`
>
> **Mijael (temperatura exterior, Azángaro)**
> * **DimensiónU1:** `pyspark/sesiones/U1_Batch_Temperatura/U1_Mijael_Temperatura_S01_S05_Batch.ipynb` (Excel simulado `data/AgroSmart_Temperatura_U1.xlsx`)
> * **DimensiónU2:** `pyspark/sesiones/Sensortemperatura/U2_Mijael_Temperatura_S06_S12_Tiempo_Real.ipynb`
>
> **Producto final U3:** presentación en `presentacion/AgroSmart_Puno_U3_Producto_Final.pptx` (31 láminas) y su guion en PDF, cuaderno `pyspark/sesiones/U3_Integracion/U3_Integracion_DataOps_S13_S14.ipynb`, `docs/hardening.md` y `scripts/auditoria_config.py`.
>
> **Pregunta central** + variable de interés + dimensión de cada integrante (cada una con DimensiónU1 batch y DimensiónU2 streaming): `docs/proyecto-sello/pregunta-general.md` y `docs/proyecto-sello/brief.md`.
>
> Novedades: carga inicial **simulada** (90 días) + histórico y tiempo real de la **API Open-Meteo**; predicción de humedad a **+1, +2 y +3 h**; dashboard Grafana en **3 partes** (61 paneles): Parte 1 Humedad (José) → Parte 2 Temperatura (Mijael) → Parte 3 operación común (`obs/grafana/dashboards/agrosmart_u2.json`); flujo **cada 2 minutos** para ambos (`iniciar_tiempo_real_2min.bat`, ver `docs/tiempo-real-2-minutos.md`); atajos `iniciar_base.bat`, `iniciar_streaming.bat`, `iniciar_streaming_mijael.bat`, `detener_todo.bat`; dimensión de Mijael con tópicos, tablas, modelo y consumer propios. Ver `documentacion/CAMBIOS_Y_VALIDACION.md`.

---

# AgroSmart Puno · Producto de Unidad 2 — Humedad del suelo

**Equipo del Proyecto Sello:** Jose Armando Mamani Poccohuanca y Mijael Yurins Coaquira Justo.  
**Dimensión U2 implementada aquí:** Jose Armando Mamani Poccohuanca — monitoreo y predicción de **humedad del suelo** a +1, +2 y +3 horas, con **humedad del aire** como única variable ambiental complementaria.

**Referencia de organización:** [repositorio `lambda26` del docente](https://github.com/262bigdata/lambda26) y [rúbrica oficial U2](https://262bigdata.github.io/lambda26/proyecto-sello/u2-producto/). No se modifica el repositorio del docente: se adapta la organización de subsistemas y las etapas S6–S12 al caso AgroSmart.

## Objetivo general

Implementar y evaluar un pipeline Big Data para monitorear y predecir la humedad del suelo en el contexto agrícola de Puno, integrando estimaciones meteorológicas de Open-Meteo, eventos empresariales **simulados** de evaluación del estado de humedad, Apache Kafka, Spark Structured Streaming y MLlib, PostgreSQL, Prometheus y Grafana para visualizar tendencias, predicciones y métricas del procesamiento.

**Alcance científico:** `soil_moisture_0_to_1cm` corresponde a humedad volumétrica modelada de suelo 0–1 cm (m³/m³ × 100 = % volumétrico); `relative_humidity_2m` es humedad relativa modelada del aire (%). No hay sensores físicos, órdenes reales de riego, recomendaciones agronómicas validadas ni control de actuadores. Los registros históricos reproducidos por Kafka son **replay**, aunque su publicación y consumo ocurren en vivo. La API no garantiza que el valor de suelo cambie mucho.

## Arquitectura orientada al docente

```text
Open-Meteo (DOS variables de humedad)
  └─ uso-agrosmart/producer/producer_api_humedad.py ──┐
                                                     ▼
                                      Kafka: humedad-telemetria
                                                     │
                 ┌───────────────────────────────────┼─────────────────────┐
                 │                                   │                     │
                 ▼                                   ▼                     ▼
  producer_evaluaciones.py        pyspark/scripts/consumer_streaming.py    consumer_verificacion.py
  (consume telemetría, publica)     (Spark Structured Streaming)             (demo offsets)
                 │                                   │
                 ▼                                   │
     Kafka: humedad-empresarial ──────────────────────┤
                                                     ▼
                         PostgreSQL: eventos, ventanas, modelos, predicciones
                                                     │
                                             obs/exporter → Prometheus
                                                     │
                                                 Grafana
```

- **S6, eventos empresariales:** una evaluación *simulada* de humedad para gestión de riego se genera a partir de cada evento meteorológico de la misma API. No inventa ventas ni volúmenes de riego. El umbral `UMBRAL_SOLO_DEMO_PCT=20` es **solo ilustrativo**, no recomendación agronómica.
- **S7, IoT/telemetría:** datos horarios modelados Open-Meteo publicados en `agrosmart-u2-humedad-telemetria`.
- **S8, consumidor persistente:** `spark-submit` procesa dos tópicos, registra eventos, ventanas de 1 h, watermark de 2 h, deduplicación y checkpoints separados.
- **S9:** Prometheus + exportador PG/Kafka, alertas, Grafana y costos en **soles (S/)**.
- **S10:** notebook Jupyter: cuatro algoritmos MLlib + baseline, tres horizontes, selección temporal y evaluación; artefactos guardados.
- **S11:** dashboard Grafana en 3 partes (**61 paneles**), predicción +1/+2/+3 h de humedad y +1 h de temperatura, KPI empresarial y de humedad con predicciones y métricas de ML en la misma sesión.
- **S12:** evidencias, GitHub, MkDocs, pitch y demo individual de José.

## Carpetas en el mismo orden organizativo

```text
AgroSmart_Puno_U2_FINAL/
├── .github/workflows/              # publicación MkDocs
├── docs/                           # MkDocs: brief + S6...S12 + rúbrica
├── kafka/                          # broker, Kafka UI, kafka exporter
│   └── compose.yml
├── obs/                            # Prometheus, Grafana, exportador PG, alertas
│   ├── compose.yml
│   ├── prometheus/
│   └── grafana/
├── overrides/                      # personalizaciones futuras
├── pyspark/
│   ├── compose.yml                 # PostgreSQL + Jupyter
│   ├── compose.kafka.yml           # consumer persistente con perfil streaming
│   ├── scripts/                     # consumer_streaming.py, costos_pen.py
│   ├── sql/schema.sql
│   └── sesiones/Sensorhumedad/
│       ├── 01_entrenamiento_y_verificacion_humedad.ipynb
│       ├── datos/  ├── modelos/  ├── resultados/  ├── checkpoints/ └── evidencias/
├── uso-agrosmart/
│   ├── compose.yml
│   ├── producer/                     # consulta API y evaluaciones de humedad
│   ├── consumer/                     # consumidores simples de verificación Kafka
│   └── contratos/                    # contratos JSON Schema por tópico
├── pruebas/                          # pruebas unitarias sin Docker
├── documentacion/                   # guías paso a paso y checklist
├── .env.example
└── mkdocs.yml
```

## Paso a paso desde Windows PowerShell

**Previo:** Docker Desktop con Compose, Git, internet para Open-Meteo/Maven. Usa una carpeta independiente, por ejemplo `D:\C9\Big Data\AgroSmart_Puno_U2_FINAL`. Si el proyecto anterior sigue levantado y ocupa los mismos puertos, **detén solamente ese proyecto** desde su propia carpeta (`docker compose stop`); no elimines sus volúmenes. Todos los comandos siguientes se ejecutan en **la raíz de este proyecto nuevo**.

### Paso 0 — Credenciales y diagnóstico

```powershell
Copy-Item .env.example .env
notepad .env
# Cambia POSTGRES_PASSWORD, GRAFANA_ADMIN_PASSWORD, JUPYTER_TOKEN.
# Nunca publiques .env en GitHub.
docker compose version
docker info
```

### Paso 1 — Kafka, Kafka UI y Kafka Exporter

```powershell
docker compose --env-file .env -f kafka/compose.yml config -q
docker compose --env-file .env -f kafka/compose.yml up -d
docker compose --env-file .env -f kafka/compose.yml ps
```

**Kafka UI:** http://localhost:48086  
**Kafka desde contenedores:** `kafka:9092`  
**Kafka desde Windows:** `localhost:49093` (no es una página web).

### Paso 2 — PostgreSQL + Jupyter con Spark 3.5

```powershell
docker compose --env-file .env -f pyspark/compose.yml -f pyspark/compose.kafka.yml config -q
docker compose --env-file .env -f pyspark/compose.yml -f pyspark/compose.kafka.yml up -d --build postgres jupyter
```

**Jupyter:** http://localhost:4489/lab (token definido en `.env`).  
**PostgreSQL:** `localhost:15432`, DB `agrosmart_u2`, dentro de Docker `postgres:5432`.

Abre `Sensorhumedad/01_entrenamiento_y_verificacion_humedad.ipynb`, ejecuta **etapas 0–4 en orden**. Esto descarga el histórico de la API, muestra gráficos reales de sus valores, entrena y compara **Regresión Lineal, Random Forest, Árbol de Decisión y Gradient Boosted Trees** para cada horizonte, contrasta con persistencia y guarda 3 modelos Spark. **No arranques todavía el consumidor streaming si los modelos no están guardados.**

> Mejoramos un problema anterior: el Jupyter de entrenamiento NO carga el conector Kafka (no lo necesita). El proceso `spark-consumer`, separado, lo incluye mediante `spark-submit` y usa su propio directorio Ivy con permisos de escritura.

### Paso 3 — Crear ambos tópicos Kafka

```powershell
docker compose --env-file .env -f uso-agrosmart/compose.yml --profile herramientas run --rm inicializar-topicos
```

Esperado: aparecen `agrosmart-u2-humedad-telemetria` y `agrosmart-u2-humedad-empresarial` en Kafka UI. Una partición/replicación 1 es **laboratorio**, no producción HA.

### Paso 4 — Iniciar consumer Spark (S8/S10) y derivador empresarial (S6)

```powershell
docker compose --env-file .env -f pyspark/compose.yml -f pyspark/compose.kafka.yml --profile streaming up -d spark-consumer
docker compose --env-file .env -f uso-agrosmart/compose.yml --profile flujo up -d producer-evaluaciones
```

Verificar logs en PowerShell:

```powershell
docker compose --env-file .env -f pyspark/compose.yml -f pyspark/compose.kafka.yml logs --tail=80 spark-consumer
docker compose --env-file .env -f uso-agrosmart/compose.yml logs --tail=40 producer-evaluaciones
```

El consumer debe iniciar **3 consultas**: `telemetria`, `empresarial`, `ventanas`. Si aparece `ClassNotFoundException KafkaSourceProvider` o un problema de Maven, revisa la sección *Diagnóstico*; no sustituyas automáticamente la versión de Spark.

### Paso 5 — Producer de la MISMA API, replay académico de 72 horas

```powershell
docker compose --env-file .env -f uso-agrosmart/compose.yml --profile replay run --rm producer-api-replay
```

El productor hace una consulta a Open-Meteo, conserva un archivo `datos/bronze/open_meteo_*.json`, publica registros de humedad del suelo y aire y obtiene offsets. El proceso `producer-evaluaciones` deriva de cada registro su evaluación empresarial simulada y la publica al segundo tópico. El Spark Consumer guarda ambos flujos en PostgreSQL e infiere +1/+2/+3 h.

**Consumer sencillo de verificación de Kafka:**

```powershell
docker compose --env-file .env -f uso-agrosmart/compose.yml --profile verificacion run --rm consumer-verificacion
docker compose --env-file .env -f uso-agrosmart/compose.yml --profile verificacion run --rm consumer-verificacion-empresa
```

Consulta el progreso SQL en el notebook, etapa 6, o en la base de datos. **Los conteos esperados de la primera demo son orientativos**: 72 telemetrías, hasta 72 evaluaciones, hasta 216 predicciones, ventanas horarias. Replays repetidos con los mismos identificadores no duplican registros válidos.

### Paso 6 — Prueba de watermark y checkpoints

Cuando el watermark ya haya avanzado con los datos históricos ordenados:

```powershell
docker compose --env-file .env -f uso-agrosmart/compose.yml --profile pruebas run --rm producer-evento-tardio
```

Comprueba que Kafka recibió el evento con un offset nuevo, y busca ese `evento_id` en `eventos_telemetria`. Si el watermark avanzó lo suficiente, no debería insertarse. **Si sí se insertó**, revisa `lastProgress` y si la prueba fue aplicada después del avance de watermark; no afirmes que pasó sin comprobarlo. Los checkpoints físicos estarán en `pyspark/sesiones/Sensorhumedad/checkpoints/{telemetria,empresarial,ventanas}`. Detén/reanuda `spark-consumer` sin eliminar esos directorios y verifica ausencia de duplicados.

### Paso 7 — Prometheus, Grafana y observabilidad

```powershell
docker compose --env-file .env -f obs/compose.yml up -d --build
```

| Servicio | URL o dirección | Validación |
|---|---|---|
| Kafka UI | http://localhost:48086 | 2 tópicos y offsets |
| Jupyter | http://localhost:4489/lab | MLlib y PostgreSQL |
| Prometheus | http://localhost:9095/targets | `agrosmart_exporter` y `kafka_exporter` UP |
| Exportador PostgreSQL | http://localhost:9202/metrics | Métricas `agrosmart_*` |
| Exportador Kafka | http://localhost:49309/metrics | Métricas del broker/tópicos |
| Grafana | http://localhost:3300 | Dashboard en 3 partes (61 paneles): humedad → temperatura → común |
| PostgreSQL | `localhost:15432` | Tablas de humedad y modelos |

En Prometheus consulta `up{job="agrosmart_exporter"}`, `agrosmart_exportador_consulta_ok`, `agrosmart_consulta_activa` y `agrosmart_duracion_lote_ms`. En Grafana abre **Dashboards → AgroSmart U2 → AgroSmart Puno U2 — Humedad del suelo + aire | BI/ML y Observabilidad**; rango **Last 90 days** para replay. Incluye KPIs y predicciones **en el mismo dashboard**. No confundas datos retrospectivos con predicciones prospectivas.

### Paso 8 — Costos en soles S/ con mediciones y escenarios

Desde **Jupyter → New → Terminal**:

```bash
python /home/jovyan/agrosmart-repo/pyspark/scripts/costos_pen.py --tarifa-computo-hora 0.30 --tarifa-gb-mes 0.40
```

Muestra también `docker stats --no-stream` desde PowerShell y el volumen de registros. Las tarifas S/0.30/h y S/0.40/GB-mes son **supuestos ilustrativos editables**, NO precios comerciales verificados. El informe incluye escenarios de 1, 24 y 240 eventos/h y se guarda en `resultados/costos_pen.json` y en la tabla `escenarios_costos`, visible en Grafana.

### Paso 9 — Seguimiento periódico (no replay) y evaluación de inferencia prospectiva

```powershell
docker compose --env-file .env -f uso-agrosmart/compose.yml --profile continuo up -d producer-api-continuo
```

Consulta la API cada 10 minutos y evita publicar respuestas horarias idénticas. Puede no llegar un nuevo evento durante bastante tiempo: **no significa que Kafka esté caído**. Debes comprobar el campo `es_retro` de `predicciones_humedad`; los pronósticos de replay serán retrospectivos. Los de modo continuo deben evaluarse conforme lleguen estimaciones posteriores. No afirmar generalización a sensores físicos.

### Paso 10 — MkDocs, GitHub y sustentación individual

Abre **Terminal** en Jupyter:

```bash
mkdocs serve -f /home/jovyan/agrosmart-repo/mkdocs.yml --dev-addr 0.0.0.0:8000
```

Abre http://localhost:8008. Publica tu repositorio propio y activa **Settings → Pages → GitHub Actions**; el workflow construye MkDocs. Agrega topics académicos (por ejemplo `big-data`, `spark-structured-streaming`, `kafka`, `prometheus`, `grafana`, `humedad-suelo`, `open-meteo`) y demuestra commits. Captura todas las pruebas exigidas en `docs/proyecto-sello/u2-evidencias.md`. La nota depende de verificación en vivo y sustentación, no solo del ZIP.

## Big Data histórico y volumen de datos de la API

| Dimensión | Forecast API (últimos 60 días) | Historical API ERA5 (2012–2026) | Total descargado de Open-Meteo |
|---|---:|---:|---:|
| Humedad del suelo · José (Puno) | 1 447 | 130 320 | **131 767** |
| Temperatura · Mijael (Azángaro) | 1 447 | 130 320 | **131 767** |
| **Total** | 2 894 | 260 640 | **263 534** |

- Cuaderno `pyspark/sesiones/Historico_BigData/U3_BigData_Historico_OpenMeteo.ipynb`: descarga, Bronze → Silver → Gold (Parquet por año/mes) y modelos +1 h con Spark MLlib.
- Los cuadernos U2 cargan ambos orígenes (sección 2.1b), los registran en la tabla `api_descargas` y Grafana los muestra en «Descargados de Open-Meteo».
- El histórico de suelo es la capa 0–7 cm (la de 0–1 cm no existe en el archivo ERA5): no se mezcla con el entrenamiento del modelo de streaming.
- Todo se vuelve a ejecutar con `ejecutar_todo_cuadernos.bat` (U1 → histórico → U2 → reinicio de consumidores → U3).

## Apagar sin perder evidencias

```powershell
docker compose --env-file .env -f uso-agrosmart/compose.yml stop
docker compose --env-file .env -f obs/compose.yml stop
docker compose --env-file .env -f pyspark/compose.yml -f pyspark/compose.kafka.yml stop
docker compose --env-file .env -f kafka/compose.yml stop
```

**Jamás uses `down -v` para cerrar el trabajo si deseas conservar PostgreSQL/Kafka/Grafana.**

## Limitaciones de validación de esta entrega

Se incluyen configuración, scripts, tests offline, notebook, dashboard, consultas, documentación y guías. **El autor del paquete no puede ejecutar Docker de tu laptop desde aquí**: el funcionamiento conjunto, las pruebas de watermark, las alertas en Firing/Normal, la URL pública de MkDocs y las métricas reales deben confirmarse en tu entorno. Algunos resultados pueden depender de la disponibilidad de Open-Meteo y Maven.
