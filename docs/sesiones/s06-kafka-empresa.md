# S6 · Ingesta empresarial de humedad

**José · DimensiónU2.** Esta sesión aporta al monitoreo y predicción en tiempo real de la humedad.

**Tema único:** evaluación **simulada** de humedad del suelo para apoyar la revisión manual del riego. `producer_evaluaciones.py` consume el tópico meteorológico y produce `agrosmart-u2-humedad-empresarial`. No contiene ventas, inventarios ni litros ficticios.

**Contrato:** `uso-agrosmart/contratos/empresarial.schema.json`. Campos principales: `evento_id`, `evento_telemetria_id`, `fecha_evento`, `ubicacion`, `tipo=evaluacion_humedad`, `estado`, ambas humedades y `umbral_demo_pct`.

**Verificación:** en Kafka UI mostrar offset y contrato; ejecutar `consumer_verificacion_empresa.py`; consultar `SELECT estado,COUNT(*) FROM eventos_empresariales GROUP BY estado;`. El umbral 20 % es solo para generar un evento empresarial reproducible, no una indicación clínica/agronómica.
