@echo off
chcp 65001 >nul
cd /d "%~dp0"
title AgroSmart Puno - Cuadernos U2 (Jose y Mijael)
set "DC=docker compose --env-file .env -f pyspark/compose.yml -f pyspark/compose.kafka.yml"
%DC% exec -T jupyter bash /home/jovyan/work/ejecutar_cuadernos.sh Sensorhumedad/U2_AgroSmart_S06_S12_Humedad_Tiempo_Real.ipynb Sensortemperatura/U2_Mijael_Temperatura_S06_S12_Tiempo_Real.ipynb > "evidencias\ejecucion_u2.txt" 2>&1
type "evidencias\ejecucion_u2.txt" | findstr /b "OK FALLO"
timeout /t 15 >nul
