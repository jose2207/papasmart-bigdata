# AgroSmart Puno · Proyecto Sello Big Data (Unidades 1, 2 y 3)

**Pregunta central:** ¿cómo anticipar a corto plazo las condiciones meteorológicas de riesgo agrícola del altiplano de Puno —estrés hídrico del suelo y heladas— a partir de datos de Open-Meteo? ([detalle](proyecto-sello/pregunta-general.md))

**Equipo y dimensiones** (cada una con DimensiónU1 batch y DimensiónU2 streaming):
- **José Armando Mamani Poccohuanca** — *humedad del suelo* (predicción a +1, +2 y +3 h).
- **Mijael Yurins Coaquira Justo** — *temperatura exterior en Azángaro* (predicción a +1 h con alerta de helada).

Este sitio adopta la navegación del [repositorio del docente](https://github.com/262bigdata/lambda26) con una implementación propia de S1 a S12. Consulta la **matriz de cumplimiento** y las **evidencias** antes de presentar el proyecto.

No se usan sensores físicos, datos de ventas ni otras dimensiones. Tanto la humedad del suelo 0–1 cm como la humedad relativa del aire provienen de **Open-Meteo** (modelos). Los eventos de evaluación empresarial de humedad son **simulados**; no son riegos reales ni recomendaciones agronómicas.

## Ruta de lectura

1. [Pregunta central y dimensiones](proyecto-sello/pregunta-general.md)
2. [Brief oficial completado](proyecto-sello/brief.md)
3. [Datos: real, simulado e inyectado](datos.md)
4. [Arquitectura](arquitectura.md)
5. **José** — DimensiónU1 (S1–S5): [índice](unidad1/index.md) · DimensiónU2 (S6–S12): menú lateral
6. **Mijael** — [índice](mijael/index.md) · [DimensiónU1](mijael/dimension-u1.md) · [DimensiónU2](mijael/dimension-u2.md)
7. [Matriz de rúbrica U2](proyecto-sello/u2-producto.md) y [Evidencias S12](proyecto-sello/u2-evidencias.md)
8. [Guía de ejecución en CMD](guia-ejecucion.md)

**Volumen:** **263 534 registros descargados de la API Open-Meteo** (131 767 por dimensión: 1 447 recientes + 130 320 históricos 2012–2026), procesados con Spark ([Big Data histórico](big-data-historico.md)).

**Cumplimiento del producto U3:** [lista de componentes, rúbrica y autoevaluación](proyecto-sello/u3-producto.md).

**Estado:** sistema completo de las tres unidades, levantado y verificado en la laptop del equipo (19 contenedores, flujo cada 2 minutos en vivo). El [informe del proyecto](informe-proyecto.md) reúne las 14 secciones pedidas; las evidencias están en [pruebas y evidencias](pruebas-evidencias.md).

## Producto final (Unidad 3)
Sistema Big Data **end-to-end** (batch + streaming + BI/ML + observabilidad) para el riesgo agroclimático del altiplano de Puno, con DataOps verificable y hardening.
**Curso:** Big Data · Universidad Peruana Unión, Juliaca · 2026-2 · Grupo 11 · Sección GU
**Repositorio:** [https://github.com/jose2207/papasmart-bigdata](https://github.com/jose2207/papasmart-bigdata) · **Este sitio:** [https://jose2207.github.io/papasmart-bigdata/](https://jose2207.github.io/papasmart-bigdata/)
**Integrantes:** Jose Armando Mamani Poccohuanca (humedad) y Mijael Yurins Coaquira Justo (temperatura).
Ver [instalación](instalacion.md), [uso](uso.md), [matriz de trazabilidad](proyecto-sello/matriz-trazabilidad.md), [DataOps](dataops.md), [hardening](hardening.md) y [demo](demo.md).

