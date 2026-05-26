@echo off
REM Run this as Administrator (right-click -> Run as administrator)
echo Opening firewall port 5000 for the dashboard...
netsh advfirewall firewall add rule name="PowerBI WhatsApp Dashboard" dir=in action=allow protocol=TCP localport=5000
echo.
echo Done. Other devices on your network can now open:
echo   http://192.168.0.205:5000
echo.
pause
