# Mijael · DimensiónU2 — Temperatura en tiempo real (streaming, S6–S12)

**Indicador U2:** temperatura en vivo, dato por dato, y su **predicción a +1 h** actualizándose junto con ella, con alerta de helada.

| Sesión | Qué se hace | Componente |
|---|---|---|
| S6 | Evaluaciones simuladas de riesgo de helada (`alerta_helada` ≤ 0 °C, `vigilancia` 0–3 °C, `normal`) a Kafka | `producer_evaluaciones_temperatura.py`, tópico `…temperatura-empresarial` |
| S7 | API `temperature_2m` → Kafka (replay y continuo) + **carga inicial simulada** de 90 días | `producer_api_temperatura.py`, `simulador_temperatura.py` |
| S8 | Spark Structured Streaming: 3 consultas (`temp_telemetria`, `temp_empresarial`, `temp_ventanas`), ventana 1 h, watermark 2 h, checkpoints | `consumer_streaming_temperatura.py` |
| S9 | Prometheus (`agrosmart_temperatura_*`), alertas técnicas, costos en S/ | exporter + `alerts.yml` |
| S10 | 4 algoritmos vs. persistencia (prueba = API real); inferencia por evento y pronóstico «ahora» | cuaderno U2, `modelos/temperatura_1h` |
| S11 | Fila **07 · MIJAEL · TEMPERATURA** del Grafana común | `obs/grafana/dashboards/agrosmart_u2.json` |
| S12 | Evidencias (`evidencia_u2_temperatura.json`), ficha U2 y checklist | cuaderno U2 |

**Variables del modelo desplegado:** temperatura actual, `hora_seno`, `hora_coseno` (el streaming procesa un evento a la vez; sin lags).
**Tablas:** `eventos_temperatura`, `eventos_empresariales_temperatura`, `predicciones_temperatura`, `ventanas_temperatura`, `metricas_modelo_temperatura`, `comparacion_modelos_temperatura` (más `metricas_pipeline` compartida).
**Aviso:** el umbral de helada es didáctico y no sustituye alertas oficiales.
