@echo off
title We Xipantu - Sistema de registro
cd /d "%~dp0"

if not exist "venv\Scripts\python.exe" (
    echo No se encontro el entorno de Python ^(carpeta venv^).
    echo Contacta a soporte tecnico.
    pause
    exit /b 1
)

echo Iniciando el sistema We Xipantu...
echo No cierres esta ventana mientras uses el sistema.
echo Para salir, simplemente cierra esta ventana.
echo.

start "" /min powershell -NoProfile -Command "Start-Sleep -Seconds 2; Start-Process 'http://127.0.0.1:8000/'"

"venv\Scripts\python.exe" manage.py runserver 127.0.0.1:8000

echo.
echo El sistema se ha detenido.
pause >nul
