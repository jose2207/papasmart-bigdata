# Producto de Unidad 2 — cumplimiento exigible

**Fuente de requisitos:** [rúbrica oficial U2](https://262bigdata.github.io/lambda26/proyecto-sello/u2-producto/). Esta matriz documenta **qué código existe y qué debe demostrarse**; no adjudica por anticipado la nota A.

| Nº | Peso | Objetivo nivel A | Implementación disponible | Evidencia que falta ejecutar/guardar |
|---|---:|---|---|---|
| 1 Kafka empresarial S6 | 12 % | Publicado/consumido en vivo; contrato y tópico documentados | `producer_evaluaciones.py`, JSON Schema y consumidor Spark/consumer de inspección | Kafka UI + offsets del tópico empresarial y filas PG nuevas |
| 2 IoT/sensores S7 | 10 % | Telemetría integrada y volumen verificado | API Open-Meteo, `producer_api_humedad.py`, tópico y esquema de humedad | 72 eventos de replay/continuo + procedencia visible; aclarar que no son sensores físicos |
| 3 Spark Streaming S8 | 14 % | Ventanas, watermark, checkpoints en vivo | `consumer_streaming.py`: 3 consultas, ventanas 1h, watermark 2h y checkpoints | SQL ventanas, prueba tardío y reinicio sin duplicados |
| 4 Observabilidad S9 | 12 % | Métricas correlacionadas y dashboard operativo | Prometheus, Kafka exporter, PG exporter, alertas, Grafana | `UP`, 3 consultas activas, alertas y screenshots Firing→Normal |
| 5 Costos/escalado S9 | 8 % | Estimación justificada por volumen | `costos_pen.py` con observaciones PG y 3 escenarios en S/ | `docker stats`, tamaño medio, tasas reales y discusión de escalado |
| 6 BI/ML S11 | 12 % | KPIs streaming demostrados en vivo | dashboard Grafana v4 en 3 partes (61 paneles) y 2 fuentes | KPIs de evaluación empresarial e inferencia visibles juntos en el mismo tablero |
| 7 Modelos S10 | 12 % | Modelo validado e integrado BI | Notebook cuatro algoritmos, tres horizontes, baseline, artefactos Spark | RMSE/MAE/R² y métricas prospectivas si las hay, sin afirmar generalización física |
| 8 Sustentación S12 | 20 % | Aporte individual y seis subaspectos | MkDocs, README, guion y estructura GitHub | Demo ante el docente, repo publicado, site MkDocs URL real |

## Sustentación — seis subaspectos obligatorios

1. **Aporte individual:** José ejecuta y explica su dimensión U2; no atribuye código ajeno.
2. **Comunicación y orden:** presenta objetivo, arquitectura, demo y conclusiones con tiempos claros.
3. **Presentación personal:** puntualidad, vestimenta e imagen adecuadas, actitud profesional y respeto según rúbrica.
4. **Repositorio y estándares:** topics académicos, commits, seguridad de secretos, reproducibilidad.
5. **MkDocs:** publicado, navegable y alineado a estas secciones.
6. **Pitch/demo:** breve evolución desde U1 y PowerPoint que precede a la demostración técnica.

**Nota:** el texto de la rúbrica muestra `Σ(Peso × Puntos)/100 ×20`, pese a que la escala A/B/C/D ya es 20/15/10/5. Para una nota sobre 20, la suma ponderada `Σ(Peso × Puntos)/100` es la interpretación dimensionalmente consistente; confirmar con el docente antes de reportar notas.
