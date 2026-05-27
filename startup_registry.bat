@echo off
REM Add ReportFlow to Windows startup registry for automatic start after reboot
echo Adding ReportFlow to Windows startup...

set "SERVICE_PATH=%~dp0start_service.bat"

REM Add registry entry for auto-start
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "ReportFlow" /t REG_SZ /d "\"%SERVICE_PATH%\"" /f

echo.
echo ✅ ReportFlow added to Windows startup!
echo.
echo The system will now:
echo 1. Start automatically when Windows boots
echo 2. Run 24/7 in the background
echo 3. Restart automatically if it crashes
echo 4. Survive system reboots
echo.

pause