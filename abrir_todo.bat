@echo off
chcp 65001 >nul
setlocal EnableExtensions
cd /d "%~dp0"
title AgroSmart Puno - Inicio completo
set "ENVF=--env-file .env"
if not exist .env ( echo Falta el archivo .env & pause & exit /b 1 )

echo ==============================================================
echo   AGROSMART PUNO - INICIO COMPLETO DEL SISTEMA
echo ==============================================================

echo [1/6] Verificando Docker Desktop ...
docker info >nul 2>&1
if errorlevel 1 (
  start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
  echo      Iniciando Docker Desktop, espera ...
  :esperar_docker
  timeout /t 5 >nul
  docker info >nul 2>&1 || goto :esperar_docker
)
echo      Docker listo.

echo [2/6] Kafka (KRaft) y Kafka UI ...
docker compose %ENVF% -f kafka/compose.yml up -d || goto :error

echo [3/6] PostgreSQL, Jupyter y consumidores Spark Structured Streaming ...
docker compose %ENVF% -f pyspark/compose.yml -f pyspark/compose.kafka.yml up -d postgres jupyter || goto :error
docker compose %ENVF% -f pyspark/compose.yml -f pyspark/compose.kafka.yml --profile streaming --profile streaming-temperatura up -d spark-consumer spark-consumer-temperatura || goto :error

echo [4/6] Productores cada 2 min y productores de evaluaciones ...
docker compose %ENVF% -f uso-agrosmart/compose.yml --profile tiempo-real-2min --profile flujo --profile flujo-temperatura up -d producer-humedad-2min producer-temperatura-2min producer-evaluaciones producer-evaluaciones-temperatura || goto :error

echo [5/6] Observabilidad: Prometheus, Pushgateway, exporter y Grafana ...
docker compose %ENVF% -f obs/compose.yml up -d || goto :error

echo      Esperando 30 s a que los servicios queden listos ...
timeout /t 30 >nul

echo [6/6] Abriendo ventanas de logs y el navegador ...
start "1 PRODUCTOR HUMEDAD (Jose)" cmd /k "color 0A & docker logs -f --tail 15 producer-humedad"
start "2 PRODUCTOR TEMPERATURA (Mijael)" cmd /k "color 06 & docker logs -f --tail 15 producer-temperatura"
start "3 SPARK HUMEDAD (Jose)" cmd /k "color 0B & docker logs -f --tail 25 spark-consumer-humedad"
start "4 SPARK TEMPERATURA (Mijael)" cmd /k "color 0E & docker logs -f --tail 25 spark-consumer-temperatura"
start "5 MENSAJES EN KAFKA" cmd /k "color 0F & call ver_mensajes_kafka.bat"

for /f "usebackq tokens=1,* delims==" %%a in (".env") do if /i "%%a"=="JUPYTER_TOKEN" set "JT=%%b"
set "CHROME=chrome"
if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" set "CHROME=%ProgramFiles%\Google\Chrome\Application\chrome.exe"
if exist "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" set "CHROME=%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
if exist "%LocalAppData%\Google\Chrome\Application\chrome.exe" set "CHROME=%LocalAppData%\Google\Chrome\Application\chrome.exe"
start "" "%CHROME%" --new-window "http://127.0.0.1:3300/d/agrosmart-presentacion?orgId=1&refresh=30s" "http://127.0.0.1:3300/d/agrosmart-puno-humedad-u2-v2?orgId=1&refresh=30s" "http://127.0.0.1:48086" "http://127.0.0.1:4489/lab?token=%JT%" "http://127.0.0.1:9095/targets" "http://127.0.0.1:9095/alerts" "http://127.0.0.1:9096"

echo.
echo LISTO. Ventanas abiertas:
echo   Chrome : Grafana ^| Kafka UI ^| Jupyter ^| Prometheus targets ^| alertas ^| Pushgateway
echo   CMD    : productores, consumidores Spark y mensajes en Kafka
echo   Para apagar todo: detener_todo.bat
docker ps --format "table {{.Names}}\t{{.Status}}"
pause
exit /b 0

:error
echo ERROR al iniciar un servicio. Revisa que Docker Desktop este abierto.
pause
exit /b 1
