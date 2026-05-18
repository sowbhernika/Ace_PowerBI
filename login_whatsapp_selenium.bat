@echo off
echo ============================================
echo   WhatsApp Web Login (Selenium + Chrome)
echo   A browser will open - scan the QR code
echo ============================================
echo.
cd /d d:\Ace_powerbi
call venv\Scripts\activate
python send_whatsapp_selenium.py --login
pause
