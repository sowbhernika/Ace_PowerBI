@echo off
echo.
echo ===========================================
echo       ReportFlow 24/7 Status Check
echo ===========================================
echo.

echo 🔍 Checking Windows Service...
sc query ReportFlowService
echo.

echo 🌐 Testing API Connection...
curl -s http://localhost:5000/api/config >nul 2>&1
if %errorLevel% EQU 0 (
    echo ✅ API is responding at http://localhost:5000
) else (
    echo ❌ API is not responding
)
echo.

echo 📋 Scheduled Tasks Status...
schtasks /query /tn "ReportFlow Monitor" | findstr "Ready Running"
schtasks /query /tn "ReportFlow Startup" | findstr "Ready Running"
echo.

echo 📊 Recent Monitor Log (last 5 lines):
if exist service_monitor.log (
    powershell "Get-Content service_monitor.log | Select-Object -Last 5"
) else (
    echo No monitor log found yet
)
echo.

echo 🔄 To restart service: python install_service.py restart
echo 🌐 Access web interface: http://localhost:5000
echo 📖 Full guide: 24x7_SETUP_GUIDE.md
echo.

pause