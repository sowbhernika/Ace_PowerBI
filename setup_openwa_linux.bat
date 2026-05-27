@echo off
echo Setting up OpenWA with Linux containers...
echo.
echo Make sure Docker is switched to Linux containers first:
echo 1. Right-click Docker Desktop icon
echo 2. Click "Switch to Linux containers..."
echo 3. Wait for restart, then run this script again
echo.

docker version | findstr "OS/Arch" | findstr "linux"
if %errorLevel% NEQ 0 (
    echo ERROR: Docker is not in Linux container mode!
    echo Please switch to Linux containers first.
    pause
    exit /b 1
)

echo ✅ Docker is in Linux container mode
echo.

echo Stopping any existing OpenWA container...
docker stop openwa-api 2>nul
docker rm openwa-api 2>nul

echo Starting OpenWA container...
docker run -d ^
    --name openwa-api ^
    --restart=always ^
    -p 2785:2785 ^
    -e API_KEY=dev-admin-key ^
    -v openwa_data:/app/data ^
    pschmitt/open-wa:latest

if %errorLevel% EQU 0 (
    echo ✅ OpenWA container started successfully!
    echo.
    echo Container Status:
    docker ps | findstr openwa
    echo.
    echo OpenWA API will be available at: http://localhost:2785
    echo.
    echo Testing connection in 10 seconds...
    timeout 10 >nul 2>&1
    curl -s http://localhost:2785/api/health || echo API not ready yet - check logs with: docker logs openwa-api
) else (
    echo ❌ Failed to start OpenWA container
    echo Check Docker logs: docker logs openwa-api
)

echo.
pause