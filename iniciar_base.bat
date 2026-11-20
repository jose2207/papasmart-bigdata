@echo off
cd /d "%~dp0"
if not exist .env ( echo Falta el archivo .env  ^(copia .env.example a .env y ajusta las claves^) & pause & exit /b 1 )
echo === 1/3 Kafka ===
docker compose --env-file .env -f kafka/compose.yml up -d || goto :error
echo === 2/3 PostgreSQL + Jupyter ===
docker compose --env-file .env -f pyspark/compose.yml -f pyspark/compose.kafka.yml up -d --build postgres jupyter || goto :error
echo === 3/3 Topicos Kafka ===
docker compose --env-file .env -f uso-agrosmart/compose.yml --profile herramientas run --rm inicializar-topicos || goto :error
echo.
echo Jupyter: http://localhost:4489/lab   ^|  Kafka UI: http://localhost:48086
echo Abre los cuadernos y entrena los modelos ANTES de iniciar_streaming.bat
pause & exit /b 0
:error
echo ERROR: revisa el mensaje anterior. & pause & exit /b 1
