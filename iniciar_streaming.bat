@echo off
cd /d "%~dp0"
if not exist "pyspark\sesiones\Sensorhumedad\modelos\humedad_3h" ( echo Faltan los modelos. Ejecuta la seccion 10.1 de la Sesion 10 del cuaderno U2 primero. & pause & exit /b 1 )
echo === Spark consumer persistente ===
docker compose --env-file .env -f pyspark/compose.yml -f pyspark/compose.kafka.yml --profile streaming up -d spark-consumer || goto :error
echo === Evaluaciones empresariales (S6) ===
docker compose --env-file .env -f uso-agrosmart/compose.yml --profile flujo up -d producer-evaluaciones || goto :error
echo === Replay de 72 h desde la API ===
docker compose --env-file .env -f uso-agrosmart/compose.yml --profile replay run --rm producer-api-replay || goto :error
echo === Tiempo real: API cada 10 min ===
docker compose --env-file .env -f uso-agrosmart/compose.yml --profile continuo up -d producer-api-continuo || goto :error
echo === Prometheus + Grafana ===
docker compose --env-file .env -f obs/compose.yml up -d --build || goto :error
echo.
echo Grafana: http://localhost:3300  ^|  Prometheus: http://localhost:9095/targets
pause & exit /b 0
:error
echo ERROR: revisa el mensaje anterior. & pause & exit /b 1
