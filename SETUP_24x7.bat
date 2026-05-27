@echo off
echo.
echo ===========================================
echo    ReportFlow 24/7 Service Installation
echo ===========================================
echo.

REM Check if running as Administrator
net session >nul 2>&1
if %errorLevel% NEQ 0 (
    echo ❌ ERROR: This script must be run as Administrator
    echo.
    echo Right-click and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

echo ✅ Running as Administrator - proceeding with setup...
echo.

echo Step 1/4: Installing dependencies...
pip install pywin32 requests
if %errorLevel% NEQ 0 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Step 2/4: Installing Windows Service...
python install_service.py install
if %errorLevel% NEQ 0 (
    echo ❌ Failed to install service
    pause
    exit /b 1
)

echo.
echo Step 3/4: Setting up auto-start...
reg add "HKLM\Software\Microsoft\Windows\CurrentVersion\Run" /v "ReportFlow" /t REG_SZ /d "\"%~dp0start_service.bat\"" /f

echo.
echo Step 4/4: Creating monitoring tasks...
schtasks /create /tn "ReportFlow Monitor" /tr "python \"%~dp0monitor_service.py\"" /sc minute /mo 5 /ru SYSTEM /f
schtasks /create /tn "ReportFlow Startup" /tr "\"%~dp0start_service.bat\"" /sc onstart /ru SYSTEM /f

echo.
echo Step 5/5: Starting the service...
python install_service.py start

echo.
echo ===========================================
echo           🚀 SETUP COMPLETE! 🚀
echo ===========================================
echo.
echo ✅ ReportFlow is now running 24/7!
echo.
echo 🌐 Access URLs:
echo   Local:   http://localhost:5000
echo   Network: http://192.168.1.10:5000
echo.
echo 🔧 Service Management:
echo   Status:  sc query ReportFlowService
echo   Start:   python install_service.py start
echo   Stop:    python install_service.py stop
echo.
echo 📊 Monitoring:
echo   - Service health checked every 5 minutes
echo   - Auto-restart on failure
echo   - Logs in service_monitor.log
echo.
echo 🔄 The system will:
echo   ✓ Start automatically when Windows boots
echo   ✓ Run 24/7 in the background  
echo   ✓ Restart automatically if it crashes
echo   ✓ Work without user login
echo.

pause