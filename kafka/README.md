# Kafka — S6 y S7 (mismo patrón de carpetas del docente)

Inicio desde la raíz: `docker compose --env-file .env -f kafka/compose.yml up -d`.

- Interno entre contenedores: `kafka:9092`; externo Windows: `localhost:49093`.
- Kafka UI: http://localhost:48086.
- Kafka Exporter: http://localhost:49309/metrics.
- Tópicos: `agrosmart-u2-humedad-telemetria` y `agrosmart-u2-humedad-empresarial`.
- Crear tópicos con `docker compose --env-file .env -f uso-agrosmart/compose.yml --profile herramientas run --rm inicializar-topicos`.
- El broker de un nodo con replicación 1 y listeners PLAINTEXT es **exclusivamente laboratorio local**. No exponer puertos fuera de localhost.
- La producción de mensajes se confirma mediante offset. El consumo se verifica por los `consumer_verificacion` y Spark; no asumir que un offset implica persistencia.
