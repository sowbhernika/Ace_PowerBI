@echo off
title Power BI WhatsApp Dashboard
echo ============================================
echo   Power BI Report Manager - Dashboard
echo   Keep this window OPEN while using it.
echo   Open http://localhost:5000 in your browser
echo ============================================
echo.
cd /d d:\Ace_powerbi
venv\Scripts\python.exe app.py
echo.
echo Server stopped. Press any key to close.
pause
