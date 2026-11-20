# S7 · Ingesta IoT/telemetría modelada

**José · DimensiónU2.** Esta sesión aporta al monitoreo y predicción en tiempo real de la humedad.

El Producer consulta `https://api.open-meteo.com/v1/forecast` para `soil_moisture_0_to_1cm` y `relative_humidity_2m`. Los resultados son **estimaciones de modelo meteorológico, no sensores físicos**.

- Contrato: `uso-agrosmart/contratos/telemetria.schema.json`.
- Tópico: `agrosmart-u2-humedad-telemetria`.
- Origen y unidades: humedad suelo m³/m³ convertido a % volumétrico; aire en %.
- Replay: 72 registros horarios históricos publicados en poco tiempo; tiempo del evento y tiempo de emisión distintos.
- Continuo: API consultada cada 600 s, publicación solo si varía el ID y la hora ya ocurrió.

**Evidencias:** JSON de Open-Meteo en Bronze, número de valores diferentes para ambas variables, Kafka UI y consumidor de prueba.
- **Carga inicial simulada:** antes de recibir la API en tiempo real se insertan 90 días simulados (`origen='simulado_carga_inicial'`, `simulador_humedad.py`) que terminan 1 h antes del histórico API. Ver [datos](../datos.md).
- **Cadencia de 2 minutos:** ver [flujo cada 2 minutos](../tiempo-real-2-minutos.md) (interpolación de estimaciones horarias; no es sensor).
