# Limitaciones y mejoras

## Limitaciones
- Los datos son **modelados** (Open-Meteo), **simulados** (carga inicial; U1 de Mijael) o **interpolados** (flujo cada 2 min); no hay sensores físicos.
- La humedad del suelo cambia poco entre horas: la **persistencia** es un rival fuerte y **en esta corrida el modelo no la supera**. RMSE de prueba (pp) de la regresión lineal frente a la persistencia: **+1 h 1,17 vs 1,10 · +2 h 1,79 vs 1,64 · +3 h 2,31 vs 2,05** (`resultados/metricas_modelo.csv`, 20-nov). Con 14 años de histórico se confirma: la persistencia gana (0,69 vs 0,72 pp). Se reporta como **resultado negativo** y no se oculta: el valor del flujo está en el monitoreo y en la tendencia, no en ganarle a la persistencia. En cambio, el modelo de temperatura sí la supera: **1,14 °C vs 1,63 °C** (−30 %) en validación, −26 % en vivo y −46 % con el histórico completo.
- Un solo nodo (sin alta disponibilidad); Kafka con un broker y sin autenticación (riesgo aceptado, ver [hardening](hardening.md)).
- Umbrales (20 % de humedad, 0 °C de helada) y costos en S/ son **didácticos**; no hay alertas oficiales ni dosis de riego.
- El histórico de suelo de Open-Meteo es la capa **0–7 cm** (no existe 0–1 cm en el archivo ERA5): se usa para volumen y análisis, no para el modelo del streaming.
- Cada integrante usa una zona distinta (Puno y Azángaro); las une la variable de interés.

## Mejoras priorizadas
1. Conectar un **sensor físico** (ESP32 + sensor capacitivo de suelo y DS18B20) al mismo contrato de Kafka.
2. Validar los modelos contra observaciones reales y recalibrar umbrales con un agrónomo.
3. Volumen y TLS/SASL en Kafka, y secretos en un gestor.
4. Pruebas de carga y clúster Spark con checkpoints compartidos.
5. Automatizar la ejecución integrada (programación diaria) con alerta si el manifiesto envejece.
