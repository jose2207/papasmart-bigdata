@echo off
chcp 65001 >nul
cd /d "%~dp0"
if not exist evidencias mkdir evidencias
set "OUT=evidencias\verificacion_ultima.txt"
echo Verificando AgroSmart Puno... (tarda 1-3 minutos). Resultado en %OUT%
> "%OUT%" echo ===== VERIFICACION AGROSMART PUNO =====
>> "%OUT%" echo Fecha y hora del equipo: %date% %time%
>> "%OUT%" echo.
>> "%OUT%" echo ===== 1. CONTENEDORES (docker ps) =====
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" >> "%OUT%" 2>&1
>> "%OUT%" echo.
>> "%OUT%" echo ===== 2. POSTGRESQL =====
docker compose --env-file .env -f pyspark/compose.yml exec -T postgres sh -c "psql -U $POSTGRES_USER -d $POSTGRES_DB" < scripts\verificacion.sql >> "%OUT%" 2>&1
>> "%OUT%" echo.
>> "%OUT%" echo ===== 3. KAFKA: TOPICOS Y OFFSETS =====
docker compose --env-file .env -f kafka/compose.yml exec -T kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server kafka:9092 --list >> "%OUT%" 2>&1
for %%T in (agrosmart-u2-humedad-telemetria agrosmart-u2-humedad-empresarial agrosmart-u2-temperatura-telemetria agrosmart-u2-temperatura-empresarial) do (
  docker compose --env-file .env -f kafka/compose.yml exec -T kafka /opt/kafka/bin/kafka-get-offsets.sh --bootstrap-server kafka:9092 --topic %%T >> "%OUT%" 2>&1
)
>> "%OUT%" echo.
>> "%OUT%" echo ===== 4. KAFKA: ULTIMOS MENSAJES (consumer de verificacion) =====
docker compose --env-file .env -f uso-agrosmart/compose.yml --profile verificacion run --rm --build consumer-verificacion >> "%OUT%" 2>&1
docker compose --env-file .env -f uso-agrosmart/compose.yml --profile verificacion-temperatura run --rm consumer-verificacion-temp >> "%OUT%" 2>&1
>> "%OUT%" echo.
>> "%OUT%" echo ===== 5. PROMETHEUS: TARGETS Y ALERTAS =====
curl.exe -s "http://127.0.0.1:9095/api/v1/targets?state=active" >> "%OUT%" 2>&1
>> "%OUT%" echo.
curl.exe -s "http://127.0.0.1:9095/api/v1/alerts" >> "%OUT%" 2>&1
>> "%OUT%" echo.
curl.exe -s "http://127.0.0.1:9095/api/v1/query?query=agrosmart_consulta_activa" >> "%OUT%" 2>&1
>> "%OUT%" echo.
curl.exe -s -o nul -w "Grafana /api/health HTTP %%{http_code}" "http://127.0.0.1:3300/api/health" >> "%OUT%" 2>&1
>> "%OUT%" echo.
>> "%OUT%" echo.
>> "%OUT%" echo ===== 6. LOGS RECIENTES DE LOS CONSUMIDORES SPARK =====
docker compose --env-file .env -f pyspark/compose.yml -f pyspark/compose.kafka.yml --profile streaming --profile streaming-temperatura logs --tail 25 spark-consumer spark-consumer-temperatura >> "%OUT%" 2>&1
>> "%OUT%" echo.
>> "%OUT%" echo ===== 7. LOGS RECIENTES DE LOS PRODUCTORES =====
docker compose --env-file .env -f uso-agrosmart/compose.yml --profile tiempo-real-2min logs --tail 8 producer-humedad-2min producer-temperatura-2min >> "%OUT%" 2>&1
>> "%OUT%" echo.
>> "%OUT%" echo ===== 8. PRUEBAS UNITARIAS Y AUDITORIA (dentro de Jupyter) =====
docker compose --env-file .env -f pyspark/compose.yml exec -T jupyter bash -lc "cd /home/jovyan/agrosmart-repo && python -m unittest discover -s pruebas 2>&1 | tail -4; python scripts/auditoria_config.py" >> "%OUT%" 2>&1
>> "%OUT%" echo.
>> "%OUT%" echo ===== 9. CONSUMO DE RECURSOS (docker stats) =====
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" >> "%OUT%" 2>&1
>> "%OUT%" echo.
>> "%OUT%" echo ===== FIN %date% %time% =====
echo Listo. Revisa %OUT%
timeout /t 5 >nul
