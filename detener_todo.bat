@echo off
cd /d "%~dp0"
docker compose --env-file .env -f uso-agrosmart/compose.yml --profile flujo --profile continuo --profile flujo-temperatura --profile continuo-temperatura --profile tiempo-real-2min stop
docker compose --env-file .env -f obs/compose.yml stop
docker compose --env-file .env -f pyspark/compose.yml -f pyspark/compose.kafka.yml --profile streaming --profile streaming-temperatura stop
docker compose --env-file .env -f kafka/compose.yml stop
echo Detenido SIN borrar volumenes ^(no uses down -v^).
pause
