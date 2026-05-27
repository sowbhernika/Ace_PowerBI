@echo off
echo Setting up Windows Task Scheduler for service monitoring...

REM Create scheduled task to monitor service every 5 minutes
schtasks /create /tn "ReportFlow Monitor" /tr "python \"%~dp0monitor_service.py\"" /sc minute /mo 5 /ru SYSTEM /f

REM Create scheduled task to start service at system startup
schtasks /create /tn "ReportFlow Startup" /tr "\"%~dp0start_service.bat\"" /sc onstart /ru SYSTEM /f

echo.
echo ✅ Scheduled tasks created:
echo.
echo 1. "ReportFlow Monitor" - Checks service health every 5 minutes
echo 2. "ReportFlow Startup" - Starts service automatically at boot
echo.

echo Verifying tasks...
schtasks /query /tn "ReportFlow Monitor"
echo.
schtasks /query /tn "ReportFlow Startup"

echo.
echo 🚀 24/7 monitoring setup complete!
echo.

pause