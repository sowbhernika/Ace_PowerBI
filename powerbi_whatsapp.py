"""
Power BI Dashboard Screenshot + WhatsApp Send (Selenium only)

First time setup:
  python powerbi_whatsapp.py --login-powerbi
  python powerbi_whatsapp.py --login-whatsapp

Daily run:
  python powerbi_whatsapp.py --from-config
"""

import sys
import os
import time
import json
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

# Config
SCREENSHOTS_DIR = Path("screenshots")
PBI_PROFILE_DIR = Path("profiles/pbi_brave_profile")
BRAVE_PATH = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
VIEWPORT_WIDTH = 1920
VIEWPORT_HEIGHT = 1080
WS = "ad1c9ec1-c5c4-4715-b882-faf093d0042b"

# All report pages with filter config
REPORT_PAGES = {
    # --- Material Matching (3 plants) - Week filter ---
    "AMC_Material_Matching": {
        "workspace": WS, "report": "3143ebc9-8f22-4bbb-878f-7ae3994b2922",
        "page": "c3057999c892e79c8330",
        "filters": ["week"],
        "enabled": True,
    },
    "AHF_Material_Matching": {
        "workspace": WS, "report": "1df5c6ee-db88-416c-b064-042aed5333a2",
        "page": "4ec7ccf471c945258609",
        "filters": ["week"],
        "enabled": True,
    },
    "APE_Material_Matching": {
        "workspace": WS, "report": "9507fedd-a744-494f-9a25-509b3bd6931d",
        "page": "29bb17a45e6647c6bd1b",
        "filters": ["week"],
        "enabled": True,
    },
    # --- Ontime Delivery - separate per plant (Company slicer) ---
    "Ontime_Delivery_AMC": {
        "workspace": WS, "report": "4f9b988f-64bc-43ba-8fb0-dbcff4295916",
        "page": "aaac226669b881008217",
        "filters": [{"type": "slicer", "label": "Company", "value": "AMC"}],
        "enabled": True,
    },
    "Ontime_Delivery_APE": {
        "workspace": WS, "report": "4f9b988f-64bc-43ba-8fb0-dbcff4295916",
        "page": "aaac226669b881008217",
        "filters": [{"type": "slicer", "label": "Company", "value": "APE"}],
        "enabled": True,
    },
    "Ontime_Delivery_AHF": {
        "workspace": WS, "report": "4f9b988f-64bc-43ba-8fb0-dbcff4295916",
        "page": "aaac226669b881008217",
        "filters": [{"type": "slicer", "label": "Company", "value": "AHF"}],
        "enabled": True,
    },
    # --- Ontime Production - all plants ---
    "Ontime_Production_FG_Bay": {
        "workspace": WS, "report": "f3d71565-b511-45b7-9bde-740d80e1f973",
        "page": "9cb90df6a9b5b7f0621c",
        "filters": [],
        "enabled": True,
    },
    # --- Baywise Output - Production (3 plants) ---
    "Baywise_AMC_Production": {
        "workspace": WS, "report": "5c830d1b-34a3-4636-9bfd-787a44bee5e0",
        "page": "ff9aa2fed9d0d6dbd750",
        "filters": ["date_to_today"],
        "enabled": True,
    },
    "Baywise_AHF_Production": {
        "workspace": WS, "report": "5c830d1b-34a3-4636-9bfd-787a44bee5e0",
        "page": "134d690a1e6c80a6b6a8",
        "filters": ["date_to_today"],
        "enabled": True,
    },
    "Baywise_APE_Production": {
        "workspace": WS, "report": "5c830d1b-34a3-4636-9bfd-787a44bee5e0",
        "page": "f1397c300b32585c4bd7",
        "filters": ["date_to_today"],
        "enabled": True,
    },
    # --- Baywise Output - Sales (3 plants) ---
    "Baywise_AMC_Sales": {
        "workspace": WS, "report": "5c830d1b-34a3-4636-9bfd-787a44bee5e0",
        "page": "87cc35ab3cb031025187",
        "filters": ["date_to_today"],
        "enabled": True,
    },
    "Baywise_AHF_Sales": {
        "workspace": WS, "report": "5c830d1b-34a3-4636-9bfd-787a44bee5e0",
        "page": "cb947835c8a546d210ba",
        "filters": ["date_to_today"],
        "enabled": True,
    },
    "Baywise_APE_Sales": {
        "workspace": WS, "report": "5c830d1b-34a3-4636-9bfd-787a44bee5e0",
        "page": "2bc45310e75761ec8039",
        "filters": ["date_to_today"],
        "enabled": True,
    },
    # --- APE-AMC Report ---
    "APE_Report_WM": {
        "workspace": WS, "report": "977bf32f-46dd-484a-8390-45b417b1e8e1",
        "page": "fd2644f3e7b3471e0cdb",
        "filters": [],
        "enabled": True,
    },
    "APE_Report_Job_Work": {
        "workspace": WS, "report": "977bf32f-46dd-484a-8390-45b417b1e8e1",
        "page": "38e39e62b1d3c56d60a5",
        "filters": [],
        "enabled": True,
    },
    # --- Ontime Purchase AMC ---
    "Ontime_Purchase_AMC_PO_Creation": {
        "workspace": "me", "report": "febfb6ca-08b4-40b0-a61c-d675f495d153",
        "page": "ReportSectione875581f54d50092167c",
        "filters": [],
        "enabled": True,
    },
    "Ontime_Purchase_AMC_Material_Wise": {
        "workspace": "me", "report": "febfb6ca-08b4-40b0-a61c-d675f495d153",
        "page": "0fe25f55b95530d5b95d",
        "filters": [],
        "enabled": True,
    },
    # --- Ontime Purchase APE ---
    "Ontime_Purchase_APE_PO_Creation": {
        "workspace": "me", "report": "7a0b33b1-ad96-41b4-a226-170473a25dfe",
        "page": "ReportSectione875581f54d50092167c",
        "filters": [],
        "enabled": True,
    },
    "Ontime_Purchase_APE_Material_Wise": {
        "workspace": "me", "report": "7a0b33b1-ad96-41b4-a226-170473a25dfe",
        "page": "97dba53009d73aa130c8",
        "filters": [],
        "enabled": True,
    },
    # --- Production Plan vs Actual ---
    "Production_Plan_vs_Actual_Material_Type": {
        "workspace": "me", "report": "7399a98f-8baf-4ea6-b0e2-22df3cc93bd6",
        "page": "f5308c51324fba683bf5",
        "filters": [],
        "enabled": True,
    },
    "Production_Plan_vs_Actual_Baywise": {
        "workspace": "me", "report": "7399a98f-8baf-4ea6-b0e2-22df3cc93bd6",
        "page": "582bb7f7652b5dc13935",
        "filters": [],
        "enabled": True,
    },
}

WHATSAPP_TARGETS = ["+919884063814"]


def kill_chrome():
    """Kill any running Chrome/chromedriver to free profile lock."""
    import subprocess
    subprocess.run(
        'powershell.exe -Command "Stop-Process -Name chrome -Force -ErrorAction SilentlyContinue; '
        'Stop-Process -Name chromedriver -Force -ErrorAction SilentlyContinue"',
        shell=True, capture_output=True, timeout=10
    )
    time.sleep(2)


def get_report_url(workspace, report, page):
    ws = workspace if workspace != "me" else "me"
    return f"https://app.powerbi.com/groups/{ws}/reports/{report}/{page}"


def get_pbi_driver(headless=True):
    options = Options()
    options.binary_location = BRAVE_PATH
    options.add_argument(f"--user-data-dir={PBI_PROFILE_DIR}")
    options.add_argument("--profile-directory=Default")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"--window-size={VIEWPORT_WIDTH},{VIEWPORT_HEIGHT}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    if headless:
        options.add_argument("--headless=new")
    return webdriver.Chrome(options=options)


def login_powerbi():
    print("Opening Power BI — please login with your credentials...")
    driver = get_pbi_driver(headless=False)
    try:
        driver.get("https://app.powerbi.com")
        print("Once you see the Power BI home page, press Enter here.")
        input("Press Enter when logged in...")
        print("Session saved.")
    finally:
        driver.quit()


# ─── Filter Functions ─────────────────────────────────────────

def is_checked(option):
    """Check if a Power BI slicer option checkbox is selected."""
    cbs = option.find_elements(By.CSS_SELECTOR, 'div.slicerCheckbox')
    if cbs:
        cls = cbs[0].get_attribute("class") or ""
        return "selected" in cls or "partiallySelected" in cls
    return False


def apply_week_filter(driver, week_count=3):
    """Select current week + next (week_count-1) weeks in the Week slicer."""
    current_week = datetime.now().isocalendar()[1]
    target_weeks = {str(current_week + i) for i in range(week_count)}
    print(f"  Week filter: selecting {sorted(target_weeks, key=int)}")

    try:
        wk = driver.find_element(By.CSS_SELECTOR, 'div[aria-label="Week"]')
    except Exception:
        print("  No Week slicer found, skipping.")
        return

    wk.click()
    time.sleep(1)

    # Set focus on first non-Select-all option
    opts = driver.find_elements(By.CSS_SELECTOR, 'div[role="option"]')
    if len(opts) > 1:
        opts[1].click()
        time.sleep(0.1)
        if is_checked(opts[1]) and opts[1].text.strip() not in target_weeks:
            opts[1].click()
            time.sleep(0.1)

    # Navigate through all items — deselect non-targets, select targets
    selected = set()
    processed = set()
    for _ in range(50):
        ActionChains(driver).send_keys(Keys.ARROW_DOWN).perform()
        time.sleep(0.15)

        for o in driver.find_elements(By.CSS_SELECTOR, 'div[role="option"]'):
            txt = o.text.strip()
            if not txt or txt == "Select all" or txt in processed:
                continue
            checked = is_checked(o)
            if txt in target_weeks:
                if not checked:
                    o.click()
                    time.sleep(0.1)
                selected.add(txt)
            else:
                if checked:
                    o.click()
                    time.sleep(0.1)
            processed.add(txt)

        if len(selected) == len(target_weeks) and len(processed) > int(max(target_weeks, key=int)):
            break

    wk = driver.find_element(By.CSS_SELECTOR, 'div[aria-label="Week"]')
    wk.click()
    time.sleep(0.5)
    print(f"  Weeks applied: {sorted(selected, key=int)}")


def apply_slicer_single(driver, slicer_label, value):
    """Select a single value in a dropdown slicer (e.g., Company = AMC)."""
    print(f"  Slicer filter: {slicer_label} = {value}")

    try:
        slicer = driver.find_element(By.CSS_SELECTOR, f'div[aria-label="{slicer_label}"]')
    except Exception:
        print(f"  Slicer '{slicer_label}' not found, skipping.")
        return

    slicer.click()
    time.sleep(1)

    # Find and click the target value
    opts = driver.find_elements(By.CSS_SELECTOR, 'div[role="option"]')
    for o in opts:
        txt = o.text.strip()
        if txt == value:
            if not is_checked(o):
                o.click()
                time.sleep(0.2)
        elif txt and txt != "Select all":
            if is_checked(o):
                o.click()
                time.sleep(0.2)

    slicer = driver.find_element(By.CSS_SELECTOR, f'div[aria-label="{slicer_label}"]')
    slicer.click()
    time.sleep(0.5)
    print(f"  {slicer_label} set to {value}")


def apply_date_filter_to_today(driver):
    """Update Date filter end date to today (start-of-month → today)."""
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.action_chains import ActionChains
    today = datetime.now()
    today_str = today.strftime("%d/%m/%Y")
    month_start_str = today.strftime("01/%m/%Y")
    print(f"  Date filter: {month_start_str} to {today_str}")

    # Click blank space to show Filters pane
    try:
        report_area = driver.find_element(By.CSS_SELECTOR, 'div[aria-label="Power BI Report"]')
        ActionChains(driver).move_to_element_with_offset(report_area, 100, 100).click().perform()
        time.sleep(2)
    except Exception:
        pass

    # Find and click the Date filter to expand it
    try:
        date_filter = driver.find_element(By.CSS_SELECTOR, 'div[aria-label^="Date is on or after"]')
        date_filter.click()
        time.sleep(2)
    except Exception:
        print("  No Date filter found, skipping.")
        return

    # Update both "on or before" date inputs to today
    inputs = driver.find_elements(By.CSS_SELECTOR,
        'input[aria-label="And show items when the value is on or before:"]')
    for inp in inputs:
        try:
            inp.click()
            inp.send_keys(Keys.CONTROL + "a")
            inp.send_keys(Keys.DELETE)
            inp.send_keys(today_str)
            inp.send_keys(Keys.TAB)
            time.sleep(0.5)
        except Exception as e:
            print(f"  Failed to update date input: {e}")

    time.sleep(2)
    print(f"  Date filter applied: end = {today_str}")


def apply_filters(driver, filters):
    """Apply all configured filters for a report page."""
    if not filters:
        return

    for f in filters:
        if f == "week":
            apply_week_filter(driver, week_count=3)
        elif f == "date_to_today":
            apply_date_filter_to_today(driver)
        elif isinstance(f, dict):
            if f["type"] == "slicer":
                apply_slicer_single(driver, f["label"], f["value"])


# ─── Screenshot ───────────────────────────────────────────────

def _take_one(driver, page_name, page_config):
    """Take screenshot of one page using an already-open driver."""
    url = get_report_url(page_config["workspace"], page_config["report"], page_config["page"])
    print(f"  {page_name}")

    driver.get(url)

    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR,
                'div.slicer-container, div.report-canvas, '
                'div[class*="visualContainer"], div[class*="report"]'))
        )
    except Exception:
        pass

    time.sleep(6)

    # Apply filters
    filters = page_config.get("filters", [])
    apply_filters(driver, filters)

    # Wait for charts to reload
    wait_time = 6 if filters else 3
    time.sleep(wait_time)

    # Hide popups
    driver.execute_script("""
        ['.bannerWrapper', '[class*="banner"]', '[class*="popup"]',
         '[class*="dialog"]', '[class*="notification"]'].forEach(function(s) {
            document.querySelectorAll(s).forEach(function(el) {
                el.style.display = 'none';
            });
        });
    """)
    time.sleep(1)

    SCREENSHOTS_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filepath = SCREENSHOTS_DIR / f"{page_name}_{timestamp}.png"
    driver.save_screenshot(str(filepath))
    print(f"    Saved: {filepath}")
    return str(filepath)


def take_screenshot(page_name, page_config):
    """Take screenshot of a single page (opens and closes browser)."""
    driver = get_pbi_driver(headless=True)
    try:
        return _take_one(driver, page_name, page_config)
    except Exception as e:
        print(f"    ERROR: {e}")
        return None
    finally:
        driver.quit()


def take_screenshots_batch(pages_dict):
    """Take screenshots of multiple pages using ONE browser session.

    pages_dict: {name: page_config, ...}
    Returns: {name: filepath_or_None, ...}
    """
    if not pages_dict:
        return {}

    print(f"Taking {len(pages_dict)} screenshots (1 browser)...")
    driver = get_pbi_driver(headless=True)
    results = {}
    try:
        for name, page_config in pages_dict.items():
            try:
                results[name] = _take_one(driver, name, page_config)
            except Exception as e:
                print(f"    ERROR {name}: {e}")
                results[name] = None
    finally:
        driver.quit()

    success = sum(1 for v in results.values() if v)
    print(f"Screenshots: {success}/{len(results)} done.")
    return results


# ─── WhatsApp Send ────────────────────────────────────────────

def send_whatsapp(filepath, targets=None, caption=""):
    """Send one image to targets (opens browser per call — use send_whatsapp_batch for bulk)."""
    from send_whatsapp_selenium import send_image
    msg = caption or f"Power BI Dashboard - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    abs_path = os.path.abspath(filepath)
    targets = targets or WHATSAPP_TARGETS

    for target in targets:
        print(f"  Sending to {target}...")
        result = send_image(abs_path, phone=target, caption=msg)
        if result:
            print(f"  Sent to {target}")
        else:
            print(f"  Failed: {target}")
        time.sleep(3)


def send_whatsapp_batch(screenshots, recipients, return_results=False):
    """Send all screenshots to all recipients using ONE browser session."""
    from send_whatsapp_openwa import send_batch

    jobs = []
    for page_name, filepath in screenshots.items():
        if not filepath:
            continue
        caption = f"{page_name.replace('_', ' ')} - {datetime.now().strftime('%d %b %Y')}"
        for phone in recipients:
            jobs.append((filepath, phone, caption))

    if not jobs:
        print("No images to send.", flush=True)
        if return_results:
            return []
        return

    print(f"\n=== Sending {len(jobs)} messages (1 browser session) ===", flush=True)
    results = send_batch(jobs)
    sys.stdout.flush()
    if return_results:
        return results


def manager_gets_report(manager_companies, report_company):
    """Return True if a manager should receive a report based on company match."""
    if not manager_companies:
        return False
    if "ALL" in manager_companies:
        return True
    if report_company == "GENERAL":
        return True  # general reports go to everyone
    return report_company in manager_companies


def send_whatsapp_routed(screenshots, report_companies, recipients, return_results=False):
    """Send each report only to managers whose companies match the report's company.

    screenshots: {report_name: filepath_or_None}
    report_companies: {report_name: "AMC"/"AHF"/"APE"/"GENERAL"}
    recipients: [{name, phone, companies:[...]}]
    """
    from send_whatsapp_openwa import send_batch

    jobs = []       # (filepath, phone, caption) for send_batch
    job_meta = []   # (report_name, phone, filepath, caption) parallel to jobs
    for page_name, filepath in screenshots.items():
        if not filepath:
            continue
        rcompany = report_companies.get(page_name, "GENERAL")
        caption = f"{page_name.replace('_', ' ')} - {datetime.now().strftime('%d %b %Y')}"
        for r in recipients:
            phone = r.get("phone") if isinstance(r, dict) else r
            companies = r.get("companies", ["ALL"]) if isinstance(r, dict) else ["ALL"]
            if phone and manager_gets_report(companies, rcompany):
                jobs.append((filepath, phone, caption))
                job_meta.append((page_name, phone, filepath, caption))

    if not jobs:
        print("No matching report/recipient pairs to send.", flush=True)
        return [] if return_results else None

    print(f"\n=== Routed send: {len(jobs)} messages (company-matched) ===", flush=True)
    results = send_batch(jobs)  # [(phone, ok), ...] in same order as jobs
    sys.stdout.flush()

    # Build detailed results: [(report, phone, filepath, caption, ok)]
    detailed = []
    for (page_name, phone, filepath, caption), (_, ok) in zip(job_meta, results):
        detailed.append((page_name, phone, filepath, caption, ok))

    if return_results:
        return detailed


def send_jobs(jobs):
    """Re-send a specific list of (filepath, phone, caption) jobs. Used by retry."""
    from send_whatsapp_openwa import send_batch
    if not jobs:
        return []
    print(f"\n=== Retry send: {len(jobs)} messages ===", flush=True)
    results = send_batch(jobs)
    sys.stdout.flush()
    return results


# ─── Run Modes ────────────────────────────────────────────────

def run_from_config():
    """Run using config.json (used by scheduled task and web UI)."""
    config_file = Path("config.json")
    if not config_file.exists():
        print("ERROR: config.json not found.")
        sys.exit(1)

    with open(config_file, "r") as f:
        config = json.load(f)

    enabled_pages = {k: v for k, v in config["report_pages"].items() if v.get("enabled")}
    # Only enabled managers (disabled ones are temporarily skipped)
    recipients = [r for r in config.get("recipients", [])
                  if not isinstance(r, dict) or r.get("enabled", True)]

    if not enabled_pages:
        print("No reports enabled.")
        return
    if not recipients:
        print("No recipients configured.")
        return

    print(f"=== {len(enabled_pages)} report(s) -> {len(recipients)} recipient(s) ===")

    # Kill any running Chrome to free profile lock
    kill_chrome()

    # Step 1: Take all screenshots in ONE browser
    screenshots = take_screenshots_batch(enabled_pages)

    success = sum(1 for v in screenshots.values() if v)
    if success == 0:
        print("ERROR: No screenshots taken. Nothing to send.")
        return

    # Step 2: Route each report to matching-company managers
    time.sleep(2)
    report_companies = {k: v.get("company", "GENERAL") for k, v in enabled_pages.items()}
    send_whatsapp_routed(screenshots, report_companies, recipients)

    print("\nAll done!")


def main():
    print(f"=== Power BI Screenshot + WhatsApp === {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    for page_name, page_config in REPORT_PAGES.items():
        if not page_config.get("enabled", True):
            continue
        print(f"\n--- {page_name} ---")
        filepath = take_screenshot(page_name, page_config)
        if filepath:
            caption = f"{page_name.replace('_', ' ')} - {datetime.now().strftime('%d %b %Y')}"
            send_whatsapp(filepath, caption=caption)
    print("\nAll done!")


if __name__ == "__main__":
    if "--login-powerbi" in sys.argv:
        login_powerbi()
    elif "--login-whatsapp" in sys.argv:
        from send_whatsapp_selenium import login_whatsapp
        login_whatsapp()
    elif "--from-config" in sys.argv:
        run_from_config()
    else:
        main()
