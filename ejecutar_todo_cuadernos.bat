@echo off
chcp 65001 >nul
setlocal EnableExtensions
cd /d "%~dp0"
title AgroSmart Puno - Ejecucion completa de los cuadernos
set "DC=docker compose --env-file .env -f pyspark/compose.yml -f pyspark/compose.kafka.yml"
set "LOG=%CD%\evidencias\ejecucion_completa.txt"
echo ===== EJECUCION COMPLETA %date% %time% ===== > "%LOG%"
del /q "pyspark\sesiones\resumen_ejecucion.txt" 2>nul
echo Ejecutando U1, U2, historico y U3. Tarda entre 15 y 40 minutos. No cierres esta ventana.

echo [1/4] U1 batch, Big Data historico y U2 tiempo real (Jose y Mijael) ...
%DC% exec -T jupyter bash /home/jovyan/work/ejecutar_cuadernos.sh U1_Batch_Humedad/U1_AgroSmart_S01_S05_Humedad_Batch.ipynb U1_Batch_Temperatura/U1_Mijael_Temperatura_S01_S05_Batch.ipynb Historico_BigData/U3_BigData_Historico_OpenMeteo.ipynb Sensorhumedad/U2_AgroSmart_S06_S12_Humedad_Tiempo_Real.ipynb Sensortemperatura/U2_Mijael_Temperatura_S06_S12_Tiempo_Real.ipynb >> "%LOG%" 2>&1

echo [2/4] Reiniciando los consumidores Spark para cargar los modelos recien entrenados ...
%DC% --profile streaming --profile streaming-temperatura restart spark-consumer spark-consumer-temperatura >> "%LOG%" 2>&1
echo      Esperando 4 minutos a que lleguen datos nuevos con los modelos actualizados ...
timeout /t 240 >nul

echo [3/4] U3 integracion DataOps ...
%DC% exec -T jupyter bash /home/jovyan/work/ejecutar_cuadernos.sh U3_Integracion/U3_Integracion_DataOps_S13_S14.ipynb >> "%LOG%" 2>&1

echo [4/4] Resumen:
type "pyspark\sesiones\resumen_ejecucion.txt"
type "pyspark\sesiones\resumen_ejecucion.txt" >> "%LOG%"
echo FIN >> "%LOG%"
pause
