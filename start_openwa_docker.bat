@echo off
echo Starting OpenWA Docker Container for 24/7 Operation...
echo.

REM Stop and remove existing container if it exists
docker stop openwa-api 2>nul
docker rm openwa-api 2>nul

echo Starting OpenWA container...
docker run -d ^
    --name openwa-api ^
    --restart=always ^
    -p 2785:2785 ^
    -e API_KEY=dev-admin-key ^
    -v openwa_data:/app/data ^
    open-wa/wa-automate:latest

if %errorLevel% EQU 0 (
    echo ✅ OpenWA Docker container started successfully!
    echo.
    echo Container will:
    echo   ✓ Auto-restart if it crashes
    echo   ✓ Start automatically when Docker starts
    echo   ✓ Run 24/7 in the background
    echo.
    echo OpenWA API will be available at: http://localhost:2785
) else (
    echo ❌ Failed to start OpenWA container
    echo Trying alternative image...
    
    docker run -d ^
        --name openwa-api ^
        --restart=always ^
        -p 2785:2785 ^
        -e API_KEY=dev-admin-key ^
        -v openwa_data:/app/data ^
        smashah/open-wa:latest
    
    if %errorLevel% EQU 0 (
        echo ✅ OpenWA started with alternative image!
    ) else (
        echo ❌ Both images failed. Check Docker and try manual setup.
    )
)

echo.
echo Checking container status...
docker ps | findstr openwa-api

echo.
pause