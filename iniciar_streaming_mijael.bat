@echo off
cd /d "%~dp0"
if not exist "pyspark\sesiones\Sensortemperatura\modelos\temperatura_1h" ( echo Falta el modelo de temperatura. Ejecuta la seccion 10.1 de la Sesion 10 del cuaderno U2 de Mijael primero. & pause & exit /b 1 )
echo === Spark consumer de temperatura ===
docker compose --env-file .env -f pyspark/compose.yml -f pyspark/compose.kafka.yml --profile streaming-temperatura up -d spark-consumer-temperatura || goto :error
echo === Evaluaciones de riesgo de helada (S6) ===
docker compose --env-file .env -f uso-agrosmart/compose.yml --profile flujo-temperatura up -d producer-evaluaciones-temperatura || goto :error
echo === Replay de 72 h desde la API ===
docker compose --env-file .env -f uso-agrosmart/compose.yml --profile replay-temperatura run --rm producer-temp-replay || goto :error
echo === Tiempo real: API cada 10 min ===
docker compose --env-file .env -f uso-agrosmart/compose.yml --profile continuo-temperatura up -d producer-temp-continuo || goto :error
echo === Prometheus + Grafana ===
docker compose --env-file .env -f obs/compose.yml up -d --build || goto :error
echo.
echo Grafana: http://localhost:3300 (fila 07 - Temperatura)  ^|  Prometheus: http://localhost:9095/targets
pause & exit /b 0
:error
echo ERROR: revisa el mensaje anterior. & pause & exit /b 1
