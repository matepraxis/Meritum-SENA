@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>&1
if errorlevel 1 (
    echo ERROR: Instala Python 3.12 o 3.13 desde python.org y habilita el launcher py.
    pause
    exit /b 1
)
if not exist .venv\Scripts\python.exe (
    echo Creando entorno virtual...
    py -3 -m venv .venv
    if errorlevel 1 goto :error
)
echo Instalando dependencias. Solo requiere Internet la primera vez...
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto :error
.venv\Scripts\python.exe manage.py migrate --noinput
if errorlevel 1 goto :error
.venv\Scripts\python.exe manage.py cargar_demo
if errorlevel 1 goto :error
echo.
echo MERITUM-SENA: abre http://127.0.0.1:8000 en el navegador
echo Presiona Ctrl+C para detener el servidor.
.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
exit /b %errorlevel%
:error
echo Error durante la instalacion. Revisa los mensajes anteriores.
pause
exit /b 1
