# Flujo de datos cada 2 minutos (humedad y temperatura)

## Por qué no basta con "consultar la API cada 2 minutos"
- **Open-Meteo** entrega estimaciones de **modelo** con paso **horario**. Su resolución de 15 minutos existe solo para pocas variables y en Europa central; la **humedad del suelo** es horaria. Consultar cada 2 min devolvería el mismo valor durante una hora.
- Las APIs que sí publican observaciones cada minuto corresponden a redes de estaciones de otros países (p. ej. Nueva Zelanda o Singapur) o a planes comerciales, y no traen humedad del suelo para Puno/Azángaro. OpenWeather ofrece una línea de tiempo de 1 minuto en One Call 4.0 (con clave), también basada en modelos.
- **Conclusión:** no existe una fuente gratuita de humedad del suelo *observada* cada 2 min para esta zona.

## Solución implementada
`producer_api_2min.py` (un servicio por integrante):
1. Consulta Open-Meteo (ayer + hoy + mañana) y la **cachea 10 min**.
2. Cada 2 min calcula el valor del instante por **interpolación lineal** entre las dos estimaciones horarias consecutivas que lo rodean (`interpolacion_2min.py`).
3. Publica **un evento** en el mismo tópico de telemetría, con `origen = open_meteo_interpolado_2min`, `modo_publicacion = interpolado_2min`, las horas ancla y el peso de interpolación.

| Aspecto | Detalle |
|---|---|
| Idempotencia | `evento_id` determinista por instante; reinicios sin duplicados (`ultimo_2min_*.txt`) |
| Consumers/modelos | Sin cambios; el horizonte (+1/+2/+3 h) se cuenta desde cada evento |
| Honestidad | Reconstrucción determinista; **no** agrega ruido ni variaciones; **no** es medición de sensor |
| Límite | Usa una estimación horaria *posterior* (pronóstico del modelo) como ancla superior |

## Para datos realmente observados cada 2 minutos
Instalar un **sensor físico** (ESP32 + sensor capacitivo de humedad de suelo + DS18B20/DHT22) y publicar a Kafka con el mismo contrato (`origen = sensor_fisico`).

## Comandos
```bat
docker compose --env-file .env -f uso-agrosmart/compose.yml --profile tiempo-real-2min up -d producer-humedad-2min producer-temperatura-2min
docker compose --env-file .env -f uso-agrosmart/compose.yml logs -f producer-humedad-2min producer-temperatura-2min
```
