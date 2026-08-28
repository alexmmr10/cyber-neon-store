@echo off
title Servidor Backend - Tienda Neon
:: Asegurar que el directorio de trabajo sea la carpeta donde esta este archivo .bat
cd /d "%~dp0"
cls
echo ========================================================
echo   INICIANDO SERVIDOR BACKEND FASTAPI - TIENDA NEON
echo ========================================================
echo.
echo [INFO] Directorio actual: %cd%
echo [INFO] Iniciando main.py...
echo.

set PYTHON_EXE=C:\Users\alexm\AppData\Local\Programs\Python\Python312\python.exe

if exist "%PYTHON_EXE%" (
    "%PYTHON_EXE%" main.py
) else (
    python main.py
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Ocurrio un problema al ejecutar el servidor.
)

pause
