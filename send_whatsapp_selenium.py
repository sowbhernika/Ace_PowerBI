"""
Send images via WhatsApp Web using Selenium.
First run: python send_whatsapp_selenium.py --login  (scan QR code once)
After that: python send_whatsapp_selenium.py <image_path> [phone] [caption]
"""

import sys
import os
import time
import random
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def human_delay(min_s=1.5, max_s=4.0):
    """Random delay to mimic human behavior."""
    time.sleep(random.uniform(min_s, max_s))

WA_PROFILE_DIR = Path("d:/Ace_powerbi/wa_chrome_profile")
PHONE_TARGET = "+919884063814"
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"


def get_driver(headless=False):
    options = Options()
    options.binary_location = CHROME_PATH
    options.add_argument(f"--user-data-dir={WA_PROFILE_DIR}")
    options.add_argument("--profile-directory=Default")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    return webdriver.Chrome(options=options)


def login_whatsapp():
    print("Opening WhatsApp Web — please scan the QR code...")
    driver = get_driver(headless=False)
    try:
        driver.get("https://web.whatsapp.com")
        print("Waiting for WhatsApp to load (scan QR if needed)...")
        WebDriverWait(driver, 180).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[aria-label="Chat list"]'))
        )
        print("WhatsApp logged in! Session saved.")
        time.sleep(3)
        print("Closing browser in 5 seconds...")
        time.sleep(5)
    finally:
        driver.quit()


def _send_to_chat(driver, image_path, phone):
    """Send one image to one phone using an already-open driver."""
    clean_phone = phone.replace("+", "").replace(" ", "").replace("-", "")
    driver.get(f"https://web.whatsapp.com/send?phone={clean_phone}")
    human_delay(2.0, 4.0)

    # Wait for chat to load — accept either Attach button OR message input
    attach_selectors = (
        'button[aria-label="Attach"], '
        'div[aria-label="Attach"], '
        '[data-icon="plus"], '
        '[data-icon="clip"], '
        '[data-icon="attach-menu-plus"]'
    )
    WebDriverWait(driver, 45).until(
        EC.presence_of_element_located((By.CSS_SELECTOR,
            attach_selectors + ', div[aria-label="Type a message"], footer'))
    )
    human_delay(1.5, 3.0)

    # Click attach — try multiple selectors
    attach_btn = None
    for sel in [
        'button[aria-label="Attach"]',
        'div[aria-label="Attach"]',
        '[data-icon="plus"]',
        '[data-icon="clip"]',
        '[data-icon="attach-menu-plus"]',
    ]:
        els = driver.find_elements(By.CSS_SELECTOR, sel)
        for el in els:
            if el.is_displayed():
                attach_btn = el
                break
        if attach_btn:
            break
    if not attach_btn:
        raise Exception(f"Attach button not found for {phone}")

    # Intercept file input BEFORE clicking attach
    driver.execute_script('''
        if (!window.__fileInputIntercepted) {
            window.__fileInputIntercepted = true;
            var origCreate = document.createElement.bind(document);
            document.createElement = function(tag) {
                var el = origCreate(tag);
                if (tag.toLowerCase() === 'input') {
                    setTimeout(function() {
                        if (el.type === 'file' && !document.body.contains(el)) {
                            el.id = '__intercepted_file_input';
                            el.style.position = 'absolute';
                            el.style.left = '-9999px';
                            document.body.appendChild(el);
                        }
                    }, 50);
                }
                return el;
            };
        }
    ''')

    attach_btn.click()
    human_delay(0.8, 1.5)

    # Click "Photos & videos"
    try:
        WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR,
                'div[role="menuitem"][aria-label="Photos & videos"]'))
        ).click()
    except Exception:
        driver.find_element(By.XPATH, '//span[contains(text(), "Photos")]').click()
    human_delay(1.0, 2.0)

    # Upload file — wait up to 5 seconds for intercepted input to appear
    file_input = None
    for _ in range(10):
        try:
            file_input = driver.find_element(By.ID, '__intercepted_file_input')
            break
        except Exception:
            time.sleep(0.5)
    if not file_input:
        raise Exception(f"File input not intercepted for {phone}")
    file_input.send_keys(image_path)
    human_delay(3.0, 5.0)  # wait for image to fully load in preview

    # Wait for send button — try multiple selectors as WhatsApp UI changes
    send_btn = None
    send_selectors = [
        'div[aria-label="Send"]',
        'button[aria-label="Send"]',
        'span[data-icon="send"]',
        'span[data-icon="wds-ic-send-filled"]',
        '[data-testid="send"]',
        'div[role="button"][aria-label="Send"]',
    ]
    for _ in range(15):  # wait up to 15 seconds
        for sel in send_selectors:
            try:
                els = driver.find_elements(By.CSS_SELECTOR, sel)
                for el in els:
                    if el.is_displayed():
                        send_btn = el
                        break
                if send_btn:
                    break
            except Exception:
                continue
        if send_btn:
            break
        time.sleep(1)

    if not send_btn:
        # Try keyboard shortcut as fallback
        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.common.action_chains import ActionChains
        ActionChains(driver).send_keys(Keys.ENTER).perform()
    else:
        try:
            send_btn.click()
        except Exception:
            # Try clicking parent button if span/icon
            try:
                parent = send_btn.find_element(By.XPATH, './ancestor::button | ./ancestor::div[@role="button"]')
                parent.click()
            except Exception:
                # JavaScript click as fallback
                driver.execute_script("arguments[0].click();", send_btn)

    human_delay(3.0, 5.0)  # wait for send to complete


def send_image(image_path, phone=None, caption=""):
    """Send one image to one phone. Opens and closes browser each time."""
    target = phone or PHONE_TARGET
    image_path = os.path.abspath(image_path)
    if not os.path.exists(image_path):
        print(f"ERROR: Image not found: {image_path}")
        return False

    print(f"Sending to {target}...")
    driver = get_driver(headless=False)
    try:
        _send_to_chat(driver, image_path, target)
        print(f"Sent to {target}!")
        return True
    except Exception as e:
        print(f"ERROR sending to {target}: {e}")
        return False
    finally:
        driver.quit()


def send_batch(jobs):
    """Send multiple images efficiently using ONE browser session.

    jobs: list of (image_path, phone, caption) tuples
    Returns: list of (phone, success) results
    """
    if not jobs:
        return []

    print(f"Batch sending {len(jobs)} message(s)...")
    # Visible mode — headless mode breaks WhatsApp Web deeplinks
    driver = get_driver(headless=False)
    results = []
    try:
        # Load WhatsApp once
        driver.get("https://web.whatsapp.com")
        try:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[aria-label="Chat list"]'))
            )
        except Exception:
            print("ERROR: WhatsApp session expired. Run --login.")
            return [(j[1], False) for j in jobs]

        print("WhatsApp ready.")

        for i, (image_path, phone, caption) in enumerate(jobs):
            image_path = os.path.abspath(image_path)
            if not os.path.exists(image_path):
                print(f"  Skip: {image_path} not found", flush=True)
                results.append((phone, False))
                continue
            try:
                _send_to_chat(driver, image_path, phone)
                print(f"  [{i+1}/{len(jobs)}] Sent to {phone}", flush=True)
                results.append((phone, True))
            except Exception as e:
                err_type = type(e).__name__
                err_msg = str(e)[:150]
                page_title = ''
                try:
                    page_title = driver.title[:80]
                except Exception:
                    pass
                # Save debug screenshot
                debug_path = f"d:/Ace_powerbi/screenshots/wa_fail_{phone.replace('+','')}_{i}.png"
                try:
                    driver.save_screenshot(debug_path)
                except Exception:
                    pass
                print(f"  [{i+1}/{len(jobs)}] FAILED {phone}: {err_type}: {err_msg or '(empty)'} | page='{page_title}' | debug={debug_path}", flush=True)
                results.append((phone, False))

            # Human-like gap between messages (longer every few messages)
            if i < len(jobs) - 1:
                if (i + 1) % 5 == 0:
                    # Longer pause every 5 messages
                    human_delay(8.0, 15.0)
                else:
                    human_delay(3.0, 7.0)

    finally:
        driver.quit()

    print(f"Batch done: {sum(1 for _,s in results if s)}/{len(results)} sent.")
    return results


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--login":
        login_whatsapp()
    elif len(sys.argv) > 1:
        image = sys.argv[1]
        phone = sys.argv[2] if len(sys.argv) > 2 else PHONE_TARGET
        caption = sys.argv[3] if len(sys.argv) > 3 else ""
        send_image(image, phone, caption)
    else:
        print("Usage:")
        print("  python send_whatsapp_selenium.py --login")
        print("  python send_whatsapp_selenium.py <image> [phone] [caption]")
