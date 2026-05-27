"""
Test script to verify Brave browser integration with Selenium
"""
import sys
import os
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

def test_brave_selenium():
    """Test if Brave browser works with Selenium"""
    print("Testing Brave browser with Selenium...")
    
    # Set up Brave browser options
    BRAVE_PATH = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
    PROFILE_DIR = Path("profiles/test_brave_profile")
    CHROMEDRIVER_PATH = Path("./chromedriver-144.exe").resolve()
    
    # Create profile directory if it doesn't exist
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    
    options = Options()
    options.binary_location = BRAVE_PATH
    options.add_argument(f"--user-data-dir={PROFILE_DIR}")
    options.add_argument("--profile-directory=Default")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    # Set up ChromeDriver service
    service = Service(executable_path=str(CHROMEDRIVER_PATH))
    
    driver = None
    try:
        print("Starting Brave browser...")
        driver = webdriver.Chrome(service=service, options=options)
        
        print("Navigating to test page...")
        driver.get("https://www.google.com")
        
        print(f"Page title: {driver.title}")
        print("Brave browser integration successful!")
        
        return True
        
    except Exception as e:
        print(f"Error testing Brave browser: {e}")
        return False
        
    finally:
        if driver:
            print("Closing browser...")
            driver.quit()

if __name__ == "__main__":
    success = test_brave_selenium()
    sys.exit(0 if success else 1)