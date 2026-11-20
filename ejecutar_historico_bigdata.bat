@echo off
chcp 65001 >nul
setlocal EnableExtensions
cd /d "%~dp0"
title AgroSmart Puno - Big Data historico (Open-Meteo 2012-2026)
set "LOG=%CD%\evidencias\historico_bigdata.txt"
echo ===== HISTORICO BIG DATA %date% %time% ===== > "%LOG%"
echo Descargando ~14 anios de datos horarios reales y procesandolos con Spark.
echo Puede tardar entre 5 y 20 minutos. No cierres esta ventana.
echo.
docker compose --env-file .env -f pyspark/compose.yml -f pyspark/compose.kafka.yml up -d jupyter >> "%LOG%" 2>&1
docker compose --env-file .env -f pyspark/compose.yml -f pyspark/compose.kafka.yml exec -T jupyter jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=7200 /home/jovyan/work/Historico_BigData/U3_BigData_Historico_OpenMeteo.ipynb >> "%LOG%" 2>&1
if errorlevel 1 goto :error
echo OK >> "%LOG%"
echo.
echo LISTO. Resultados en pyspark\sesiones\Historico_BigData\resultados\resumen_historico.json
type "pyspark\sesiones\Historico_BigData\resultados\resumen_historico.json" | findstr /i "filas_gold silver bronze"
pause
exit /b 0
:error
echo ERROR >> "%LOG%"
echo ERROR: revisa evidencias\historico_bigdata.txt
type "%LOG%"
pause
exit /b 1
