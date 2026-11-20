@echo off
chcp 65001 >nul
setlocal EnableExtensions
cd /d "%~dp0"
title Reparar acceso a Grafana y productores
for /f "usebackq tokens=1,* delims==" %%a in (".env") do (
  if /i "%%a"=="GRAFANA_ADMIN_PASSWORD" set "GPW=%%b"
  if /i "%%a"=="GRAFANA_ADMIN_USER" set "GUSR=%%b"
)
echo [1/3] Restableciendo la contraseña de Grafana con la del archivo .env ...
docker compose --env-file .env -f obs/compose.yml exec -T grafana grafana cli admin reset-admin-password "%GPW%" || goto :error
echo      Usuario: %GUSR%   (la contraseña es la de GRAFANA_ADMIN_PASSWORD en .env)

echo [2/3] Reconstruyendo los productores cada 2 min (sin el mensaje de refresco del API) ...
docker compose --env-file .env -f uso-agrosmart/compose.yml --profile tiempo-real-2min up -d --build producer-humedad-2min producer-temperatura-2min || goto :error

echo [3/3] Abriendo de nuevo las ventanas de los productores ...
start "1 PRODUCTOR HUMEDAD (Jose)" cmd /k "color 0A & docker logs -f --tail 15 producer-humedad"
start "2 PRODUCTOR TEMPERATURA (Mijael)" cmd /k "color 06 & docker logs -f --tail 15 producer-temperatura"
echo.
echo LISTO. Entra a Grafana en http://127.0.0.1:3300 con el usuario %GUSR%.
pause
exit /b 0
:error
echo ERROR: revisa que Docker Desktop y los contenedores esten encendidos.
pause
exit /b 1
