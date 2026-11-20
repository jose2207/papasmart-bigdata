# Módulos o funcionalidades

| Módulo | Funcionalidad | Problema que resuelve | Dueño |
|---|---|---|---|
| Batch Spark (U1) | Lectura, calidad (−999, nulos, duplicados), Parquet particionado, modelo base | Histórico confiable para describir y entrenar | José (humedad) · Mijael (temperatura) |
| Ingesta Kafka (S6–S7) | Productores de la API, evaluaciones simuladas, flujo cada 2 min, contratos JSON | Eventos en vivo con idempotencia | José · Mijael |
| Streaming Spark (S8) | 3 consultas por integrante: eventos + inferencia, empresarial, ventanas de 1 h (watermark 2 h) | Procesar y predecir al llegar cada dato | José · Mijael |
| Modelos (S10) | 4 algoritmos MLlib vs. persistencia (+1/+2/+3 h humedad; +1 h temperatura) | Anticipar la variable | José · Mijael |
| Observabilidad (S9) | Prometheus, exporter, alertas técnicas, costos en S/ | Saber si el sistema funciona y cuánto cuesta | Común |
| BI en Grafana (S11) | Tablero único: filas 01–06 (humedad), 07 (temperatura), 08 (DataOps) | Una sola historia de riesgo agroclimático | Común |
| DataOps y hardening (U3) | Healthchecks, esperas, compuertas, manifiesto, auditoría, CI | Ejecución verificable y repetible | Común |

El detalle por sesión está en las secciones de cada integrante.
