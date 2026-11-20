@echo off
cd /d "%~dp0"
chcp 65001 >nul
if not exist evidencias mkdir evidencias
echo === Hora de Peru: correccion de consumidores Spark y reparacion de datos ===
echo.
echo [1/4] Deteniendo consumidores Spark...
docker compose --env-file .env -f pyspark/compose.yml -f pyspark/compose.kafka.yml --profile streaming --profile streaming-temperatura stop spark-consumer spark-consumer-temperatura || goto :error
echo.
echo [2/4] Reparando datos guardados (solo si tienen el desfase de 5 h)...
docker compose --env-file .env -f pyspark/compose.yml exec -T postgres sh -c "psql -v ON_ERROR_STOP=1 -U $POSTGRES_USER -d $POSTGRES_DB" < pyspark\sql\reparar_hora_peru.sql > evidencias\reparacion_hora.txt 2>&1 || (type evidencias\reparacion_hora.txt & goto :error)
type evidencias\reparacion_hora.txt
echo.
echo [3/4] Iniciando consumidores con el codigo corregido (PostgreSQL se reinicia en hora de Peru)...
docker compose --env-file .env -f pyspark/compose.yml -f pyspark/compose.kafka.yml --profile streaming --profile streaming-temperatura up -d spark-consumer spark-consumer-temperatura || goto :error
echo.
echo [4/4] Grafana en hora de Peru...
docker compose --env-file .env -f obs/compose.yml up -d grafana || goto :error
echo.
echo Listo. Ver consumo:  docker compose --env-file .env -f pyspark/compose.yml -f pyspark/compose.kafka.yml logs -f --tail 20 spark-consumer spark-consumer-temperatura
echo Esperando 3 minutos a que los consumidores Spark procesen datos nuevos...
timeout /t 180 /nobreak
call verificar_sistema.bat
echo.
echo TODO LISTO. Puedes cerrar esta ventana.
pause & exit /b 0
:error
echo ERROR: revisa el mensaje anterior. & pause & exit /b 1
