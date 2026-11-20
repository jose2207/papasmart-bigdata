@echo off
cd /d "%~dp0"
echo === Flujo cada 2 minutos: humedad (Jose) + temperatura (Mijael) ===
echo (Open-Meteo horario + interpolacion lineal; origen = open_meteo_interpolado_2min; NO es sensor)
docker compose --env-file .env -f uso-agrosmart/compose.yml --profile tiempo-real-2min up -d producer-humedad-2min producer-temperatura-2min || goto :error
echo Para ver los eventos: docker compose --env-file .env -f uso-agrosmart/compose.yml logs -f producer-humedad-2min producer-temperatura-2min
pause & exit /b 0
:error
echo ERROR: revisa el mensaje anterior. & pause & exit /b 1
