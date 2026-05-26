@echo off
title OpenWA Launcher
echo ============================================
echo   Starting OpenWA (WhatsApp API)
echo ============================================
echo.

REM 1. Start Docker Desktop if not already running
echo [1/3] Making sure Docker Desktop is running...
tasklist /FI "IMAGENAME eq Docker Desktop.exe" | find /I "Docker Desktop.exe" >nul
if errorlevel 1 (
    echo     Launching Docker Desktop...
    start "" "D:\Docker\Docker Desktop.exe"
) else (
    echo     Docker Desktop already running.
)

REM 2. Wait for the Docker engine to be ready
echo [2/3] Waiting for Docker engine (this can take a minute)...
:waitloop
docker info >nul 2>&1
if errorlevel 1 (
    timeout /t 3 /nobreak >nul
    goto waitloop
)
echo     Docker engine is ready.

REM 3. Start the OpenWA container
echo [3/3] Starting OpenWA container...
cd /d d:\Ace_powerbi\OpenWA
docker compose -f docker-compose.dev.yml up -d openwa

echo.
echo ============================================
echo   OpenWA is starting up.
echo   API:  http://localhost:2785
echo   The WhatsApp session reconnects automatically.
echo ============================================
echo.
echo You can close this window. Press any key to exit.
pause >nul
