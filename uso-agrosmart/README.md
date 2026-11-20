# Caso de uso AgroSmart U2 — Producer y Consumer

Las dos variables exclusivamente son **humedad suelo 0-1 cm** y **humedad relativa del aire**, ambas modeladas por Open-Meteo. Los eventos empresariales son evaluaciones **simuladas** y se derivan de los mismos eventos telemetría; no se generan ventas, precios ni volúmenes falsos de riego.

- `producer/open_meteo_humedad.py`: obtiene, normaliza y registra procedencia de Open-Meteo.
- `producer/producer_api_humedad.py`: Producer Kafka de telemetría; modos `replay` y `continuo`.
- `producer/producer_evaluaciones.py`: Consumer telemetría + Producer del tópico empresarial, con confirmación de publicación antes de commit.
- `consumer/consumer_verificacion.py`: Consumer de inspección del tópico telemetría.
- `consumer/consumer_verificacion_empresa.py`: Consumer de inspección del empresarial.
- `producer/producer_tardio_demo.py`: prueba controlada de un evento antiguo.
- `contratos/*.schema.json`: contratos formales.

Desde raíz, tras crear Kafka:

```powershell
docker compose --env-file .env -f uso-agrosmart/compose.yml --profile herramientas run --rm inicializar-topicos
docker compose --env-file .env -f uso-agrosmart/compose.yml --profile flujo up -d producer-evaluaciones
docker compose --env-file .env -f uso-agrosmart/compose.yml --profile replay run --rm producer-api-replay
docker compose --env-file .env -f uso-agrosmart/compose.yml --profile verificacion run --rm consumer-verificacion
docker compose --env-file .env -f uso-agrosmart/compose.yml --profile verificacion run --rm consumer-verificacion-empresa
```

**Modo continuo:** `docker compose --env-file .env -f uso-agrosmart/compose.yml --profile continuo up -d producer-api-continuo`. Consulta cada 10 min y emite solo cuando aparece otro valor horario modelado. Si no cambia la API, no se inventan eventos.
