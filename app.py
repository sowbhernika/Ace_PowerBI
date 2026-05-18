"""
Flask Web UI for Power BI WhatsApp Manager.
Run: python app.py
Open: http://localhost:5000
"""

import json
import os
import subprocess
import threading
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_file

from powerbi_whatsapp import take_screenshot, take_screenshots_batch, send_whatsapp, get_report_url, kill_chrome

app = Flask(__name__)

CONFIG_FILE = Path("d:/Ace_powerbi/config.json")
SCREENSHOTS_DIR = Path("d:/Ace_powerbi/screenshots")
TASK_NAME = "PowerBI_WhatsApp_Report"
PYTHON_EXE = str(Path("d:/Ace_powerbi/venv/Scripts/python.exe"))
SCRIPT_PATH = str(Path("d:/Ace_powerbi/powerbi_whatsapp.py"))

# Lock to prevent concurrent Selenium sessions
screenshot_lock = threading.Lock()
send_lock = threading.Lock()

# Track background task status
task_status = {"running": False, "message": "", "progress": ""}


def default_config():
    """Build default config from powerbi_whatsapp.py REPORT_PAGES."""
    from powerbi_whatsapp import REPORT_PAGES
    return {
        "report_pages": REPORT_PAGES,
        "recipients": ["+919884063814"],
        "schedule": {
            "type": "daily",
            "time": "08:00",
            "days": [],
            "one_time_date": None,
        },
    }


def load_config():
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return default_config()


def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def get_latest_thumbnail(page_name):
    """Find the most recent screenshot for a given page."""
    matches = sorted(SCREENSHOTS_DIR.glob(f"{page_name}_*.png"), key=os.path.getmtime, reverse=True)
    return str(matches[0]) if matches else None


# ─── Routes ──────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/config", methods=["GET"])
def get_config():
    return jsonify(load_config())


@app.route("/api/config", methods=["POST"])
def update_config():
    config = request.json
    save_config(config)
    return jsonify({"status": "ok"})


@app.route("/api/thumbnails", methods=["GET"])
def get_thumbnails():
    """Return which pages have thumbnails available."""
    config = load_config()
    result = {}
    for name in config["report_pages"]:
        thumb = get_latest_thumbnail(name)
        result[name] = f"/thumbnail/{name}" if thumb else None
    return jsonify(result)


@app.route("/thumbnail/<page_name>")
def serve_thumbnail(page_name):
    thumb = get_latest_thumbnail(page_name)
    if not thumb:
        return "No screenshot available", 404
    return send_file(thumb, mimetype="image/png")


@app.route("/api/screenshot/<page_name>", methods=["POST"])
def screenshot_one(page_name):
    """Take a screenshot of a single report page."""
    config = load_config()
    page_config = config["report_pages"].get(page_name)
    if not page_config:
        return jsonify({"error": "Page not found"}), 404

    try:
        with screenshot_lock:
            kill_chrome()
            filepath = take_screenshot(page_name, page_config)
        if filepath:
            return jsonify({"status": "ok", "file": filepath})
        return jsonify({"error": "Screenshot failed. Make sure Power BI login is valid."}), 500
    except Exception as e:
        return jsonify({"error": f"Screenshot error: {str(e)[:200]}"}), 500


@app.route("/api/screenshot-all", methods=["POST"])
def screenshot_all():
    """Take screenshots of ALL report pages (for previews)."""
    config = load_config()
    results = {}

    try:
        with screenshot_lock:
            kill_chrome()
            results = take_screenshots_batch(config["report_pages"])
    except Exception as e:
        return jsonify({"error": f"Screenshot error: {str(e)[:200]}"}), 500

    return jsonify({"status": "ok", "results": results})


@app.route("/api/send-now", methods=["POST"])
def send_now():
    """Send enabled reports to all recipients right now."""
    config = load_config()
    enabled_pages = {k: v for k, v in config["report_pages"].items() if v.get("enabled")}
    recipients = config.get("recipients", [])

    if not enabled_pages:
        return jsonify({"error": "No reports selected"}), 400
    if not recipients:
        return jsonify({"error": "No recipients configured"}), 400

    results = {}
    import time as _time

    try:
        # Step 1: Take all screenshots in ONE browser
        with screenshot_lock:
            kill_chrome()
            screenshots = take_screenshots_batch(enabled_pages)

        # Check how many succeeded
        success_count = sum(1 for v in screenshots.values() if v)
        if success_count == 0:
            return jsonify({"error": "All screenshots failed. Re-login to Power BI."}), 500

        # Brief pause to ensure Chrome fully exits
        _time.sleep(2)

        # Step 2: Send all screenshots in ONE batch (one browser session)
        from powerbi_whatsapp import send_whatsapp_batch
        with send_lock:
            send_results = send_whatsapp_batch(screenshots, recipients, return_results=True) or []

        # Count actual successful sends
        sent_count = sum(1 for _, ok in send_results if ok)
        total_jobs = len(send_results)

        for name, filepath in screenshots.items():
            results[name] = "sent" if filepath else "screenshot failed"

        if total_jobs == 0:
            return jsonify({"error": "No messages sent. Check WhatsApp login."}), 500
        if sent_count == 0:
            return jsonify({"error": "All WhatsApp sends failed. Re-login to WhatsApp."}), 500

        return jsonify({"status": "ok", "results": results,
                        "summary": f"{sent_count}/{total_jobs} WhatsApp messages sent"})
    except Exception as e:
        return jsonify({"error": f"Send failed: {str(e)[:200]}"}), 500


@app.route("/api/schedule", methods=["POST"])
def create_schedule():
    """Create/update Windows Task Scheduler entry."""
    config = load_config()
    schedule = config.get("schedule", {})
    sched_type = schedule.get("type", "daily")
    sched_time = schedule.get("time", "08:00")
    days = schedule.get("days", [])
    one_time_date = schedule.get("one_time_date")

    task_cmd = f'"{PYTHON_EXE}" "{SCRIPT_PATH}" --from-config'

    # Build schtasks command
    base = f'schtasks /create /tn "{TASK_NAME}" /tr "{task_cmd}" /f'

    if sched_type == "daily":
        cmd = f'{base} /sc daily /st {sched_time}'
    elif sched_type == "weekdays":
        cmd = f'{base} /sc weekly /d MON,TUE,WED,THU,FRI /st {sched_time}'
    elif sched_type == "specific_days":
        if not days:
            return jsonify({"error": "No days selected"}), 400
        day_str = ",".join(days)
        cmd = f'{base} /sc weekly /d {day_str} /st {sched_time}'
    elif sched_type == "one_time":
        if not one_time_date:
            return jsonify({"error": "No date specified"}), 400
        cmd = f'{base} /sc once /st {sched_time} /sd {one_time_date}'
    else:
        return jsonify({"error": f"Unknown schedule type: {sched_type}"}), 400

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        return jsonify({"error": result.stderr or "Failed to create schedule. Try running as Administrator."}), 500

    return jsonify({"status": "ok", "message": f"Scheduled: {sched_type} at {sched_time}"})


@app.route("/api/schedule", methods=["DELETE"])
def delete_schedule():
    """Remove the scheduled task."""
    cmd = f'schtasks /delete /tn "{TASK_NAME}" /f'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        return jsonify({"error": result.stderr or "No schedule found"}), 500
    return jsonify({"status": "ok"})


@app.route("/api/schedule/status", methods=["GET"])
def schedule_status():
    """Check if a scheduled task exists."""
    cmd = f'schtasks /query /tn "{TASK_NAME}" /fo csv /nh'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0 and TASK_NAME in result.stdout:
        # Parse next run time from CSV output
        parts = result.stdout.strip().split(",")
        next_run = parts[1].strip('"') if len(parts) > 1 else "Unknown"
        status = parts[2].strip('"') if len(parts) > 2 else "Unknown"
        return jsonify({"active": True, "next_run": next_run, "status": status})
    return jsonify({"active": False})


if __name__ == "__main__":
    # Create config if not exists
    if not CONFIG_FILE.exists():
        save_config(default_config())
        print(f"Created default config: {CONFIG_FILE}")

    SCREENSHOTS_DIR.mkdir(exist_ok=True)
    print("Starting Power BI WhatsApp Manager...")
    print("Open http://localhost:5000 in your browser")
    app.run(host="0.0.0.0", port=5000, debug=False)
