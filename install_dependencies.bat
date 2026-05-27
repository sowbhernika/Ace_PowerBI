@echo off
echo Installing Windows Service Dependencies...

REM Install required packages for Windows Service
pip install pywin32

echo.
echo Installing ReportFlow as Windows Service...
echo This will allow it to run 24/7 automatically.
echo.

REM Install the service
python install_service.py install

echo.
echo Service installed successfully!
echo.
echo To start the service:
echo   python install_service.py start
echo.
echo To stop the service:
echo   python install_service.py stop
echo.
echo To remove the service:
echo   python install_service.py remove
echo.

pause