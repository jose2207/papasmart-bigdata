@echo off
chcp 65001 >nul
setlocal EnableExtensions
cd /d "%~dp0"
title AgroSmart Puno - Publicar MkDocs en GitHub Pages
set "SRC=%CD%"
set "LOG=%SRC%\evidencias\publicar_mkdocs.txt"
set "DEST=%TEMP%\papasmart-gh-pages"
echo ===== PUBLICAR MKDOCS %date% %time% ===== > "%LOG%"
echo [1/3] Construyendo el sitio con MkDocs (contenedor Jupyter) ...
if exist "pyspark\sesiones\_site" rmdir /s /q "pyspark\sesiones\_site"
docker compose --env-file .env -f pyspark/compose.yml -f pyspark/compose.kafka.yml exec -T jupyter bash -c "cd /home/jovyan/agrosmart-repo && mkdocs build --strict -d /home/jovyan/work/_site" >> "%LOG%" 2>&1 || goto :error
echo [2/3] Preparando la rama gh-pages ...
if exist "%DEST%" rmdir /s /q "%DEST%"
mkdir "%DEST%"
robocopy "%SRC%\pyspark\sesiones\_site" "%DEST%" /E /R:1 /W:1 /NFL /NDL /NJH /NJS /NP >> "%LOG%" 2>&1
if errorlevel 8 goto :error
cd /d "%DEST%"
type nul > .nojekyll
git init -q -b gh-pages >> "%LOG%" 2>&1
git config user.name "jose2207"
git config user.email "jose2207@users.noreply.github.com"
git add -A >> "%LOG%" 2>&1
git commit -q -m "Documentación MkDocs · AgroSmart Puno (Grupo 11)" >> "%LOG%" 2>&1 || goto :error
echo [3/3] Subiendo la rama gh-pages a GitHub ...
git push -f https://github.com/jose2207/papasmart-bigdata.git gh-pages >> "%LOG%" 2>&1 || goto :error
cd /d "%SRC%"
rmdir /s /q "pyspark\sesiones\_site"
echo OK >> "%LOG%"
echo.
echo LISTO: en 1-2 minutos el sitio estara en https://jose2207.github.io/papasmart-bigdata/
timeout /t 10 >nul
exit /b 0
:error
echo ERROR >> "%LOG%"
echo ERROR: revisa evidencias\publicar_mkdocs.txt
type "%LOG%"
pause
exit /b 1
