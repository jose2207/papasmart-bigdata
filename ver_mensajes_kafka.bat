@echo off
chcp 65001 >nul
cd /d "%~dp0"
title 5 MENSAJES EN KAFKA (se actualiza cada 2 min)
:bucle
cls
echo ===== ULTIMOS MENSAJES EN KAFKA  %date% %time:~0,8% =====
docker compose --env-file .env -f uso-agrosmart/compose.yml --profile verificacion run --rm consumer-verificacion python -u consumer/consumer_verificacion.py --topico agrosmart-u2-humedad-telemetria --cantidad 3
docker compose --env-file .env -f uso-agrosmart/compose.yml --profile verificacion run --rm consumer-verificacion python -u consumer/consumer_verificacion.py --topico agrosmart-u2-temperatura-telemetria --cantidad 3
echo.
echo Siguiente lectura en 2 minutos (Ctrl+C para salir) ...
timeout /t 120 >nul
goto :bucle
