@echo off
echo Starting ReportFlow Service for 24/7 operation...

REM Start the Windows service
python install_service.py start

echo.
echo ReportFlow Service started!
echo.
echo Service Status:
sc query ReportFlowService

echo.
echo The service is now running 24/7 in the background.
echo Access at: http://localhost:5000
echo.

pause