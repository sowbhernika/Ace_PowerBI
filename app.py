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
from flask_cors import CORS

from powerbi_whatsapp import take_screenshot, take_screenshots_batch, send_whatsapp, get_report_url, kill_chrome

app = Flask(__name__)
CORS(app, origins=["*"])  # Allow frontend from any domain (Cloudflare)

CONFIG_FILE = Path("config.json")
LOGS_FILE = Path("logs/logs.json")
SCREENSHOTS_DIR = Path("screenshots")
TASK_NAME = "PowerBI_WhatsApp_Report"
PYTHON_EXE = str(Path("venv/Scripts/python.exe"))
SCRIPT_PATH = str(Path("powerbi_whatsapp.py"))


def active_recipients(recipients):
    """Return only enabled recipients (disabled ones are temporarily skipped)."""
    out = []
    for r in recipients:
        if isinstance(r, dict):
            if r.get("enabled", True):  # default enabled if field missing
                out.append(r)
        else:
            out.append(r)  # plain string = always active
    return out


def recipient_phones(recipients):
    """Extract phone strings from ENABLED recipients only."""
    phones = []
    for r in active_recipients(recipients):
        if isinstance(r, dict):
            phones.append(r.get("phone", ""))
        else:
            phones.append(r)
    return [p for p in phones if p]


def load_logs():
    if LOGS_FILE.exists():
        try:
            with open(LOGS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def add_log(entry):
    logs = load_logs()
    logs.insert(0, entry)  # newest first
    logs = logs[:200]  # keep last 200 entries
    with open(LOGS_FILE, "w") as f:
        json.dump(logs, f, indent=2)

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


GATEWAY_URL = "http://localhost:2786"  # OpenWA Node gateway (whatsapp-web.js, no Docker)


@app.route("/api/connections", methods=["GET"])
def connections():
    """Report status of Power BI login and WhatsApp (gateway) connection."""
    wa = {"ok": False, "detail": "Gateway offline", "phone": "", "name": ""}
    try:
        import requests
        r = requests.get(f"{GATEWAY_URL}/api/status", timeout=6)
        if r.status_code == 200:
            d = r.json()
            st = d.get("status", "")
            if d.get("authenticated") or st in ("authenticated", "ready", "connected"):
                wa.update({"ok": True, "detail": "Connected"})
            elif d.get("has_qr") or st == "qr_ready":
                wa["detail"] = "Needs QR scan"
            else:
                wa["detail"] = f"Status: {st or 'connecting'}"
    except Exception:
        wa["detail"] = "Gateway offline — start whatsapp-gateway"

    # Power BI — saved Brave profile = logged in
    pbi_profile = Path("profiles/pbi_brave_profile/Default")
    pbi = {"ok": pbi_profile.exists(),
           "detail": "Session saved" if pbi_profile.exists() else "Not logged in"}

    return jsonify({"whatsapp": wa, "powerbi": pbi})


@app.route("/api/whatsapp/connect", methods=["POST"])
def whatsapp_connect():
    """Check/wait for the gateway WhatsApp session (auto-restores saved login)."""
    try:
        from send_whatsapp_openwa import ensure_session_ready
        if ensure_session_ready():
            return jsonify({"status": "ok", "message": "WhatsApp connected"})
        return jsonify({"error": "Not connected. Use 'Link with QR' and scan from your phone. Is the gateway running?"}), 500
    except Exception as e:
        return jsonify({"error": f"Connect failed: {str(e)[:150]}"}), 500


@app.route("/api/whatsapp/relink", methods=["POST"])
def whatsapp_relink():
    """Log out current number and produce a fresh QR for a NEW number."""
    try:
        import requests, time as _t
        requests.post(f"{GATEWAY_URL}/api/relink", timeout=10)
        # poll for the fresh QR
        for _ in range(15):
            q = requests.get(f"{GATEWAY_URL}/api/qr", timeout=8).json()
            if q.get("qr"):
                return jsonify({"qr": q["qr"]})
            _t.sleep(2)
        return jsonify({"error": "Fresh QR not ready yet — click again in a moment."}), 200
    except Exception as e:
        return jsonify({"error": f"Relink failed: {str(e)[:150]}. Is the gateway running?"}), 500


@app.route("/api/whatsapp/qr", methods=["GET"])
def whatsapp_qr():
    """Return the QR for linking, or {connected:true} if already authenticated."""
    try:
        import requests
        r = requests.get(f"{GATEWAY_URL}/api/qr", timeout=8).json()
        if r.get("authenticated"):
            return jsonify({"connected": True})
        if r.get("qr"):
            return jsonify({"connected": False, "qr": r["qr"]})
        return jsonify({"connected": False, "qr": None,
                        "error": "QR not ready yet — try again in a moment."})
    except Exception as e:
        return jsonify({"error": f"QR error: {str(e)[:150]}. Is the gateway running?"}), 500


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


# Background send job state
send_job = {"running": False, "stage": "", "message": "", "done": False,
            "ok": False, "summary": "", "cancel": False}


def _run_send():
    """Background worker: screenshots + routed WhatsApp send."""
    import time as _time
    global send_job
    config = load_config()
    enabled_pages = {k: v for k, v in config["report_pages"].items() if v.get("enabled")}
    recipients = active_recipients(config.get("recipients", []))  # only enabled managers
    phones = recipient_phones(recipients)
    started = datetime.now()

    try:
        send_job.update({"stage": "screenshots", "message": f"Capturing {len(enabled_pages)} report(s)…"})
        with screenshot_lock:
            kill_chrome()
            screenshots = take_screenshots_batch(enabled_pages)

        if send_job["cancel"]:
            send_job.update({"running": False, "done": True, "ok": False, "summary": "Cancelled"})
            return

        success_count = sum(1 for v in screenshots.values() if v)
        if success_count == 0:
            add_log({"time": started.strftime("%Y-%m-%d %H:%M:%S"),
                     "reports": list(enabled_pages.keys()), "recipients": len(phones),
                     "sent": 0, "failed": len(phones), "status": "FAILED — all screenshots failed"})
            send_job.update({"running": False, "done": True, "ok": False,
                             "summary": "All screenshots failed. Re-login to Power BI."})
            return

        _time.sleep(2)

        send_job.update({"stage": "sending", "message": "Sending via WhatsApp…"})
        from powerbi_whatsapp import send_whatsapp_routed
        report_companies = {k: v.get("company", "GENERAL") for k, v in enabled_pages.items()}
        with send_lock:
            # detailed: [(report, phone, filepath, caption, ok), ...]
            send_results = send_whatsapp_routed(
                screenshots, report_companies, recipients, return_results=True) or []

        # Build phone -> name lookup
        name_of = {}
        for r in recipients:
            if isinstance(r, dict):
                name_of[r.get("phone", "")] = r.get("name", "")

        sent_count = sum(1 for x in send_results if x[4])
        total_jobs = len(send_results)
        failures = [
            {"report": rep, "phone": ph, "name": name_of.get(ph, ""),
             "file": fp, "caption": cap}
            for (rep, ph, fp, cap, ok) in send_results if not ok
        ]
        status = "SUCCESS" if sent_count == total_jobs and total_jobs > 0 else (
            "PARTIAL" if sent_count > 0 else "FAILED")
        add_log({"time": started.strftime("%Y-%m-%d %H:%M:%S"),
                 "reports": [k for k, v in screenshots.items() if v], "recipients": len(phones),
                 "sent": sent_count, "failed": total_jobs - sent_count, "status": status,
                 "failures": failures})

        send_job.update({"running": False, "done": True, "ok": sent_count > 0,
                         "summary": f"{sent_count}/{total_jobs} WhatsApp messages sent"})
    except Exception as e:
        add_log({"time": started.strftime("%Y-%m-%d %H:%M:%S"),
                 "reports": list(enabled_pages.keys()), "recipients": len(phones),
                 "sent": 0, "failed": len(phones), "status": f"ERROR — {str(e)[:80]}"})
        send_job.update({"running": False, "done": True, "ok": False,
                         "summary": f"Send failed: {str(e)[:150]}"})


@app.route("/api/send-now", methods=["POST"])
def send_now():
    """Start sending in the background. Returns immediately."""
    global send_job
    if send_job["running"]:
        return jsonify({"error": "A send is already running."}), 409

    config = load_config()
    enabled_pages = {k: v for k, v in config["report_pages"].items() if v.get("enabled")}
    phones = recipient_phones(config.get("recipients", []))
    if not enabled_pages:
        return jsonify({"error": "No reports selected"}), 400
    if not phones:
        return jsonify({"error": "No recipients configured"}), 400

    send_job = {"running": True, "stage": "starting", "message": "Starting…",
                "done": False, "ok": False, "summary": "", "cancel": False}
    threading.Thread(target=_run_send, daemon=True).start()
    return jsonify({"status": "started"})


@app.route("/api/send-status", methods=["GET"])
def send_status():
    return jsonify(send_job)


@app.route("/api/send-cancel", methods=["POST"])
def send_cancel():
    global send_job
    send_job["cancel"] = True
    kill_chrome()
    return jsonify({"status": "cancelling"})


@app.route("/api/logs", methods=["GET"])
def get_logs():
    return jsonify(load_logs())


@app.route("/api/logs", methods=["DELETE"])
def clear_logs():
    with open(LOGS_FILE, "w") as f:
        json.dump([], f)
    return jsonify({"status": "ok"})


def _run_retry(log_index):
    """Background worker to retry failed messages from a log entry."""
    global send_job
    logs = load_logs()
    if log_index < 0 or log_index >= len(logs):
        send_job.update({"running": False, "done": True, "ok": False, "summary": "Log entry not found"})
        return
    entry = logs[log_index]
    failures = entry.get("failures", [])
    if not failures:
        send_job.update({"running": False, "done": True, "ok": False, "summary": "No failures to retry"})
        return

    try:
        # Build jobs ONLY from the recorded failures (report+phone pairs).
        # Track each failure with its index so we can map results back exactly.
        valid = [(i, f) for i, f in enumerate(failures)
                 if f.get("file") and os.path.exists(f["file"])]
        missing = len(failures) - len(valid)
        jobs = [(f["file"], f["phone"], f.get("caption", "")) for _, f in valid]

        if not jobs:
            send_job.update({"running": False, "done": True, "ok": False,
                             "summary": "Screenshot files missing — run a fresh Send instead."})
            return

        send_job.update({"stage": "sending",
                         "message": f"Resending ONLY {len(jobs)} failed message(s)…"})

        from powerbi_whatsapp import send_jobs
        with send_lock:
            results = send_jobs(jobs)  # [(phone, ok)] in same order as jobs

        # Map results back per failure index (report+phone), not by phone alone
        still_failed = []
        retried_ok = 0
        for (idx, f), (_, ok) in zip(valid, results):
            if ok:
                retried_ok += 1
            else:
                still_failed.append(f)
        # Keep failures whose screenshot was missing (couldn't retry)
        for i, f in enumerate(failures):
            if not (f.get("file") and os.path.exists(f["file"])):
                still_failed.append(f)

        entry["failures"] = still_failed
        entry["sent"] = entry.get("sent", 0) + retried_ok
        entry["failed"] = len(still_failed)
        if len(still_failed) == 0:
            entry["status"] = "SUCCESS"
        elif retried_ok > 0:
            entry["status"] = "PARTIAL"
        with open(LOGS_FILE, "w") as f:
            json.dump(logs, f, indent=2)

        note = f" ({missing} skipped — screenshot missing)" if missing else ""
        send_job.update({"running": False, "done": True, "ok": retried_ok > 0,
                         "summary": f"Retry: {retried_ok}/{len(jobs)} resent{note}"})
    except Exception as e:
        send_job.update({"running": False, "done": True, "ok": False,
                         "summary": f"Retry failed: {str(e)[:150]}"})


@app.route("/api/retry/<int:log_index>", methods=["POST"])
def retry_failed(log_index):
    """Retry the failed messages of a given log entry."""
    global send_job
    if send_job["running"]:
        return jsonify({"error": "A send is already running."}), 409
    send_job = {"running": True, "stage": "starting", "message": "Starting retry…",
                "done": False, "ok": False, "summary": "", "cancel": False}
    threading.Thread(target=_run_retry, args=(log_index,), daemon=True).start()
    return jsonify({"status": "started"})


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



@app.route("/api/connections", methods=["GET"])
def check_connections():
    """Check Power BI and WhatsApp connection status."""
    # Power BI status (always assume logged in for now)
    pbi_status = {"ok": True, "detail": "Logged in via browser profile"}
    
    # WhatsApp status via WhatsApp Web.js
    wa_status = {"ok": False, "detail": "Not connected"}
    try:
        import requests
        
        r = requests.get("http://localhost:2786/api/status", timeout=8)
        if r.status_code == 200:
            data = r.json()
            if data.get("authenticated", False):
                wa_status = {
                    "ok": True, 
                    "detail": "Connected", 
                    "status": data.get("status", "")
                }
            else:
                wa_status = {"ok": False, "detail": f"Status: {data.get('status', 'Unknown')}"}
        else:
            wa_status = {"ok": False, "detail": "WhatsApp Web.js not responding"}
    except Exception as e:
        wa_status = {"ok": False, "detail": f"Error: {str(e)[:100]}"}
    
    return jsonify({"powerbi": pbi_status, "whatsapp": wa_status})


@app.route("/api/whatsapp/qr", methods=["GET"])
def get_whatsapp_qr():
    """Get QR code for WhatsApp authentication."""
    try:
        import requests
        
        r = requests.get("http://localhost:2786/api/qr", timeout=10)
        if r.status_code == 200:
            return jsonify(r.json())
        else:
            return jsonify({
                "success": False,
                "message": "Failed to get QR code"
            }), 500
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        }), 500


@app.route("/api/whatsapp/connect", methods=["POST"])  
def connect_whatsapp():
    """Get WhatsApp connection status."""
    try:
        import requests
        
        r = requests.get("http://localhost:2786/api/status", timeout=8)
        if r.status_code == 200:
            return jsonify(r.json())
        else:
            return jsonify({
                "success": False,
                "message": "Failed to check status"
            }), 500
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        }), 500


@app.route("/api/whatsapp/relink", methods=["POST"])
def relink_whatsapp():
    """Reinitialize WhatsApp connection."""
    try:
        import requests
        
        r = requests.post("http://localhost:2786/api/relink", timeout=10)
        if r.status_code == 200:
            return jsonify(r.json())
        else:
            return jsonify({
                "success": False,
                "message": "Failed to relink"
            }), 500
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        }), 500


if __name__ == "__main__":
    # Create config if not exists
    if not CONFIG_FILE.exists():
        save_config(default_config())
        print(f"Created default config: {CONFIG_FILE}")

    SCREENSHOTS_DIR.mkdir(exist_ok=True)
    print("Starting Power BI WhatsApp Manager...")
    print("Open http://localhost:5000 in your browser")
    app.run(host="0.0.0.0", port=5001, debug=False)
