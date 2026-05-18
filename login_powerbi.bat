@echo off
echo ============================================
echo   Power BI Login (Selenium + Chrome)
echo   Login with MFA, then press Enter here
echo ============================================
echo.
cd /d d:\Ace_powerbi
call venv\Scripts\activate
python powerbi_whatsapp.py --login-powerbi
pause
