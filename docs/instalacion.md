# Instalación o ejecución

## Requisitos
- Windows con **Docker Desktop** (Engine running), 8 GB de RAM recomendados y conexión a internet (Open-Meteo y conector Spark-Kafka de Maven en la primera corrida).
- Git (opcional) y un navegador.

## Configuración (credenciales fuera del código)
1. Descomprime el proyecto y abre CMD en su raíz.
2. Copia `.env.example` a `.env` y escribe tus propias claves (`POSTGRES_PASSWORD`, `GRAFANA_ADMIN_PASSWORD`, `JUPYTER_TOKEN`). El `.env` **no se versiona**.
3. Verifica la sintaxis de Compose:
```bat
docker compose --env-file .env -f kafka/compose.yml config -q
docker compose --env-file .env -f pyspark/compose.yml -f pyspark/compose.kafka.yml config -q
```

## Arranque con esperas por salud
```bat
docker compose --env-file .env -f kafka/compose.yml up -d --wait
docker compose --env-file .env -f pyspark/compose.yml -f pyspark/compose.kafka.yml up -d --build --wait postgres jupyter
docker compose --env-file .env -f uso-agrosmart/compose.yml --profile herramientas run --rm inicializar-topicos
docker compose --env-file .env -f obs/compose.yml up -d --build --wait
```
`--wait` espera a que cada servicio con `healthcheck` esté **sano** (no solo arrancado). Atajos: `iniciar_base.bat`, `iniciar_streaming.bat`, `iniciar_streaming_mijael.bat`, `iniciar_tiempo_real_2min.bat`.

La guía completa, paso a paso y con la solución de problemas, está en [Guía de ejecución en CMD](guia-ejecucion.md).
