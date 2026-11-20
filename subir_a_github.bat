@echo off
chcp 65001 >nul
setlocal EnableExtensions
cd /d "%~dp0"
set "SRC=%CD%"
set "REPO=https://github.com/jose2207/papasmart-bigdata.git"
set "DEST=%TEMP%\papasmart-bigdata-subida"
set "LOG=%SRC%\evidencias\subida_github.txt"
if not exist "%SRC%\evidencias" mkdir "%SRC%\evidencias"
echo ===== SUBIDA A GITHUB %date% %time% ===== > "%LOG%"

echo [1/5] Clonando %REPO% ...
if exist "%DEST%" rmdir /s /q "%DEST%"
git clone "%REPO%" "%DEST%" >> "%LOG%" 2>&1 || goto :error
cd /d "%DEST%"

for /f "delims=" %%u in ('git config user.name') do set "GITUSER=%%u"
if not defined GITUSER (
  git config user.name "jose2207"
  git config user.email "jose2207@users.noreply.github.com"
)

echo [2/5] Borrando el contenido anterior del repositorio (el historial se conserva) ...
for /f "delims=" %%D in ('dir /b /a:d') do if /i not "%%D"==".git" rmdir /s /q "%%D"
for /f "delims=" %%F in ('dir /b /a:-d') do del /f /q /a "%%F"

echo [3/5] Copiando el proyecto actual (sin secretos ni temporales) ...
robocopy "%SRC%" "%DEST%" /E /XD .git "Cl*de outputs" .spark-ivy checkpoints .ipynb_checkpoints __pycache__ bronze site _site /XF .env *.pyc generar_presentacion.js subida_github.txt /R:1 /W:1 /NFL /NDL /NJH /NJS /NP >> "%LOG%" 2>&1
if errorlevel 8 goto :error

echo [4/5] Commit ...
git add -A >> "%LOG%" 2>&1
git status --short >> "%LOG%" 2>&1
git ls-files .env >> "%LOG%" 2>&1
git commit -q -F "%SRC%\scripts\mensaje_commit.txt" >> "%LOG%" 2>&1 || goto :error

echo [5/5] Push a GitHub (si aparece una ventana de inicio de sesion, acepta con tu cuenta) ...
git push origin HEAD:main >> "%LOG%" 2>&1 || goto :error
git log --oneline -3 >> "%LOG%" 2>&1
git ls-files | find /c /v "" >> "%LOG%" 2>&1
echo OK >> "%LOG%"
echo.
echo LISTO: proyecto subido a https://github.com/jose2207/papasmart-bigdata
timeout /t 8 >nul
exit /b 0

:error
echo ERROR >> "%LOG%"
echo ERROR: revisa evidencias\subida_github.txt
type "%LOG%"
pause
exit /b 1
