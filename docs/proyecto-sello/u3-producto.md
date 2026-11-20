# Producto U3 · cumplimiento, rúbrica y autoevaluación

Esta página cruza lo que pide la [plantilla del producto de Unidad 3](https://262bigdata.github.io/lambda26/proyecto-sello/u3-producto/) con lo que entrega AgroSmart Puno (Grupo 11), y deja la autoevaluación con la rúbrica oficial. Las cifras son de la ejecución completa del 20-nov-2026 (corrida U3 `20261120T060237Z`).

**Producto:** sistema Big Data distribuido end-to-end para procesamiento batch y streaming, analítica/ML, observabilidad y visualización BI, para anticipar el estrés hídrico del suelo y las heladas en el altiplano de Puno.

## 1. Componentes mínimos del producto final

| Componente exigido | Cómo lo cumple AgroSmart Puno | Evidencia |
|---|---|---|
| Problema delimitado y arquitectura justificada (Lambda o Kappa) | Arquitectura **Lambda**: histórico para entrenar y tiempo real para inferir y alertar | [Arquitectura](../arquitectura.md) · [informe §5–6](../informe-proyecto.md) |
| Pipeline batch con Spark: extracción, transformaciones, agregaciones y calidad | U1 de José y de Mijael: −999, nulos, duplicados con `Window + row_number`, imputación con respaldo | Cuadernos `U1_Batch_Humedad` y `U1_Batch_Temperatura` |
| Salida analítica eficiente y particionada (Parquet) | Gold por `anio_mes` (U1) y por `anio`/`mes` (histórico, 179 archivos por dimensión) | [Datos](../datos.md) · [Big Data histórico](../big-data-historico.md) |
| Ingesta de eventos empresariales e IoT con Kafka | 4 tópicos: telemetría y empresarial por dimensión; productores cada 2 min y evaluadores | [Flujo cada 2 minutos](../tiempo-real-2-minutos.md) |
| Spark Structured Streaming con ventanas y watermark | 2 consumidores × 3 consultas; ventanas de 1 h, watermark de 2 h, checkpoints, deduplicación | `pyspark/scripts/consumer_streaming*.py` |
| Observabilidad técnica con métricas, paneles y costos | Exportador, Prometheus (10 alertas), Pushgateway, Grafana; costos en S/ con `costos_pen.py` | [Pruebas y evidencias](../pruebas-evidencias.md) |
| Modelo ML, series de tiempo o BI | MLlib en U1, U2 e histórico; predicción +1/+2/+3 h (humedad) y +1 h con alerta de helada | [Informe §10](../informe-proyecto.md) |
| DataOps/DevOps: salud, dependencias, configuración fuera del código, ejecución integrada con compuertas y manifiesto | Healthcheck en 9 servicios, `service_healthy`, `.env`; cuaderno U3 con 24 compuertas y manifiesto JSON; CI en GitHub Actions | [DataOps](../dataops.md) |
| Revisión técnica final: checklist, no regresión y riesgos aceptados | `auditoria_config.py`, 27 pruebas, bitácora de 9 hallazgos, tabla de riesgos aceptados | [Hardening](../hardening.md) |
| Matriz de trazabilidad | Variable, dimensión de cada integrante, indicadores U1 y U2, fuente, técnica y evidencia | [Matriz](matriz-trazabilidad.md) · [informe §4](../informe-proyecto.md) |
| Evidencias reproducibles | Manifiestos por corrida, `verificacion_ultima.txt`, cuadernos ejecutados con salidas, capturas | `pyspark/sesiones/U3_Integracion/evidencias/` · `evidencias/` |
| Documentación técnica, operativa y demo | Este sitio MkDocs, informe de 14 secciones, guía de ejecución, `abrir_todo.bat`, guion de demo | [Demo](../demo.md) · [Guía CMD](../guia-ejecucion.md) |

## 2. Rúbrica (Tabla 1) · autoevaluación del equipo

| Criterio | Peso | Nivel propuesto | Evidencia concreta |
|---|---:|:---:|---|
| 1. Integración end-to-end batch, streaming y BI/ML | 20 % | **A** | El modelo entrenado por lotes se aplica en el streaming; Grafana muestra datos, predicciones y salud en un solo tablero; la corrida U3 verifica los tres flujos juntos (24/24 compuertas) |
| 2. DataOps/DevOps en empaquetado o despliegue | 15 % | **A** | Docker Compose con healthchecks y `service_healthy`, `.env`, ejecución integrada con compuertas y manifiesto, `.bat` de arranque, CI con pruebas, auditoría y `mkdocs build --strict` |
| 3. Documentación operativa completa | 15 % | **A** si el sitio está publicado; **B** mientras GitHub Pages no esté activo | MkDocs con la plantilla de la Tabla 4, informe de 14 secciones y guía paso a paso |
| 4. Hardening y revisión técnica final | 10 % | **A** | Checklist aplicado (`auditoria_config.py`: todo Cumple o Aceptado), 9 hallazgos corregidos, prueba de no regresión tras el cambio de hora, riesgos aceptados justificados |
| 5. Demo reproducible | 15 % | **B** | Demo con `abrir_todo.bat` y guion por minuto; pendiente declarado: instalación probada desde un clon limpio en otra máquina |
| 6. Sustentación técnica | 25 % | Se evalúa en vivo | Presentación de 31 láminas, guion por integrante, demo y evidencias (ver Tabla 2) |

**Nota estimada** con la fórmula oficial, suponiendo **A** en la sustentación y el sitio publicado: 0,20 × 20 + 0,15 × 20 + 0,15 × 20 + 0,10 × 20 + 0,15 × 15 + 0,25 × 20 = **19,25 / 20**. Con el sitio aún sin publicar: **18,5 / 20**.

### Subaspectos de la sustentación (Tabla 2)

| Subaspecto | Cómo se prepara |
|---|---|
| 1. Defensa técnica | Láminas 3–17: problema, arquitectura, batch, streaming, decisiones, validaciones, resultados, limitaciones y evidencias |
| 2. Comunicación y orden | Guion con tiempos (≈29 min con demo) y reparto por lámina |
| 3. Presentación personal y actitud | Responsabilidad de cada integrante el día de la sustentación |
| 4. Aporte individual | Láminas 19 y 20: dimensión, dos indicadores y una decisión propia con lo que gana y lo que cuesta |
| 5. Repositorio y estándares | Lámina 21: topics, estructura, commits y reproducibilidad |
| 6. MkDocs | Este sitio, navegable y alineado al producto |
| 7. Pitch/demo ejecutiva | Lámina 2 (pitch en 45 s) y lámina 18 (demo end-to-end de 5 min) |

## 3. Secuencia de presentación (Tabla 3) → láminas

| Orden | Momento | Lámina |
|---:|---|---|
| 1 | Título y equipo | 1 |
| 2 | Introducción ejecutiva | 2 |
| 3 | Problema y alcance | 3 (objetivos: 4) |
| 4 | Matriz de trazabilidad | 5 |
| 5 | Dimensiones por integrante | 6 |
| 6 | Arquitectura Big Data | 7 y 8 |
| 7 | Procesamiento batch | 9 y 10 (Big Data histórico) |
| 8 | Ingesta y streaming | 11 |
| 9 | Observabilidad y costos | 12 |
| 10 | Resultados BI/ML | 13 y 14 |
| — | Integración, DataOps y hardening | 15, 16 y 17 |
| 11 | Demo end-to-end | 18 |
| 12 | Aporte individual | 19 y 20 |
| 13 | Repositorio y estándares | 21 |
| 14 | Limitaciones y mejoras | 22 |

## 4. Plantilla mínima de documentación (Tabla 4) → páginas

| Sección exigida | Página |
|---|---|
| Inicio | [Inicio](../index.md) |
| Instalación o ejecución | [Instalación](../instalacion.md) · [Guía CMD](../guia-ejecucion.md) |
| Uso del sistema | [Uso](../uso.md) |
| Arquitectura o estructura | [Arquitectura](../arquitectura.md) |
| Módulos o funcionalidades | [Módulos](../modulos.md) |
| Datos | [Datos](../datos.md) · [Flujo cada 2 minutos](../tiempo-real-2-minutos.md) · [Big Data histórico](../big-data-historico.md) |
| Pruebas y evidencias | [Pruebas y evidencias](../pruebas-evidencias.md) · [DataOps](../dataops.md) · [Hardening](../hardening.md) · [Demo](../demo.md) |
| Equipo y aporte individual | [Equipo](../equipo.md) |
| Repositorio y estándares | [Repositorio](../repositorio.md) |
| Limitaciones y mejoras | [Limitaciones](../limitaciones.md) |

## 5. Informe del proyecto (Tabla 5)

El [informe del proyecto](../informe-proyecto.md) tiene las 14 secciones en el orden de la Tabla 5: portada, resumen, competencia y alcance, matriz de trazabilidad, problema y datos, arquitectura, batch, ingesta y streaming, observabilidad y costos, resultados BI/ML, integración y DataOps, repositorio y documentación, aporte individual, y limitaciones. También está en PDF en `presentacion/Informe_del_proyecto_AgroSmart_Puno_U3.pdf`.

## 6. Fortalezas y recomendaciones

**Fortalezas**

1. Integración real de los tres flujos: el mismo modelo pasa del batch al streaming y la corrida U3 verifica todo junto con 24 compuertas y un manifiesto por corrida.
2. Volumen y honestidad: 263 534 registros reales de Open-Meteo procesados con Spark, y el resultado negativo de la humedad se reporta y se explica en lugar de ocultarse.

**Recomendaciones**

1. Probar la instalación desde un clon limpio en otra máquina y publicar el sitio en GitHub Pages, para subir la demo y la documentación al nivel A.
2. Mejorar el modelo de humedad con el último valor observado como variable o prediciendo el cambio, y extender la temperatura a +2 y +3 h.
