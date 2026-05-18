@echo off
echo Opening WhatsApp Web with target chat...
cd /d d:\Ace_powerbi
venv\Scripts\python.exe -c "from selenium import webdriver; from selenium.webdriver.chrome.options import Options; o=Options(); o.binary_location=r'C:\Program Files\Google\Chrome\Application\chrome.exe'; o.add_argument('--user-data-dir=d:/Ace_powerbi/wa_chrome_profile'); o.add_argument('--profile-directory=Default'); o.add_argument('--window-size=1920,1080'); o.add_argument('--disable-blink-features=AutomationControlled'); o.add_experimental_option('excludeSwitches',['enable-automation']); d=webdriver.Chrome(options=o); d.get('https://web.whatsapp.com/send?phone=919566649907'); input('Press Enter to close...')"
