"""
WhatsApp sender using OpenWA (self-hosted WhatsApp API Gateway).
Sends images via REST API — no Selenium, no browser automation in our code.
"""

import os
import base64
import time
import subprocess
import requests

OPENWA_URL = "http://localhost:2785"
OPENWA_API_KEY = "dev-admin-key"
OPENWA_SESSION_ID = "68b091ed-1aaa-42f5-a988-4a5138a596e9"
OPENWA_CONTAINER = "openwa-api"

HEADERS = {"X-API-Key": OPENWA_API_KEY, "Content-Type": "application/json"}
READY_STATES = ("ready", "connected", "WORKING")


def _get_status():
    try:
        r = requests.get(f"{OPENWA_URL}/api/sessions/{OPENWA_SESSION_ID}",
                         headers={"X-API-Key": OPENWA_API_KEY}, timeout=10)
        return r.json().get("status", "")
    except Exception:
        return ""


def _clear_chromium_locks():
    """Remove stale Chromium SingletonLock files that block re-launch."""
    try:
        subprocess.run(
            ["docker", "exec", OPENWA_CONTAINER, "sh", "-c",
             "rm -f /app/data/sessions/session-*/Singleton* 2>/dev/null || true"],
            capture_output=True, timeout=15
        )
    except Exception as e:
        print(f"  (lock clear skipped: {e})", flush=True)


def ensure_session_ready(max_wait=90):
    """Make sure the OpenWA session is connected. Auto-reconnect if not.

    Returns True if ready, False otherwise. Safe to call before every send.
    """
    status = _get_status()
    if status in READY_STATES:
        return True

    print(f"OpenWA session not ready (status={status or 'unknown'}). Reconnecting…", flush=True)

    # Clear any stale Chromium lock from an unclean shutdown
    _clear_chromium_locks()

    # Ask OpenWA to start/reconnect the session (login token is persisted)
    try:
        requests.post(f"{OPENWA_URL}/api/sessions/{OPENWA_SESSION_ID}/start",
                      headers=HEADERS, timeout=15)
    except Exception as e:
        print(f"  start request failed: {e}", flush=True)

    # Wait for it to come up
    waited = 0
    while waited < max_wait:
        status = _get_status()
        if status in READY_STATES:
            print("OpenWA session reconnected.", flush=True)
            return True
        if status == "qr_ready":
            print("ERROR: Session needs a fresh QR scan (logged out).", flush=True)
            return False
        time.sleep(4)
        waited += 4

    print(f"ERROR: Session did not become ready within {max_wait}s (status={status}).", flush=True)
    return False


def _chat_id(phone):
    """Convert +919884063814 -> 919884063814@c.us"""
    clean = phone.replace("+", "").replace(" ", "").replace("-", "")
    return f"{clean}@c.us"


def check_session():
    """Return True if the OpenWA session is ready (auto-reconnects if not)."""
    return ensure_session_ready()


def send_image(image_path, phone=None, caption=""):
    """Send one image to one phone via OpenWA."""
    if not phone:
        print("ERROR: no phone provided")
        return False
    image_path = os.path.abspath(image_path)
    if not os.path.exists(image_path):
        print(f"ERROR: Image not found: {image_path}")
        return False

    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()

    payload = {
        "chatId": _chat_id(phone),
        "base64": b64,
        "mimetype": "image/png",
        "filename": os.path.basename(image_path),
        "caption": caption or "",
    }
    url = f"{OPENWA_URL}/api/sessions/{OPENWA_SESSION_ID}/messages/send-image"
    try:
        r = requests.post(url, headers=HEADERS, json=payload, timeout=90)
        if r.status_code in (200, 201):
            return True
        print(f"  Failed {phone}: HTTP {r.status_code} - {r.text[:150]}")
        return False
    except Exception as e:
        print(f"  Failed {phone}: {e}")
        return False


def send_batch(jobs):
    """Send multiple (image_path, phone, caption) jobs via OpenWA.

    Returns: list of (phone, success) tuples.
    """
    if not jobs:
        return []

    print(f"OpenWA batch: {len(jobs)} message(s)...", flush=True)
    if not ensure_session_ready():
        print("ERROR: OpenWA session not ready. May need a fresh QR scan.", flush=True)
        return [(j[1], False) for j in jobs]

    results = []
    for i, (image_path, phone, caption) in enumerate(jobs):
        ok = send_image(image_path, phone, caption)
        print(f"  [{i+1}/{len(jobs)}] {'sent' if ok else 'FAILED'} -> {phone}", flush=True)
        results.append((phone, ok))
        if i < len(jobs) - 1:
            time.sleep(2)  # small gap between messages

    success = sum(1 for _, ok in results if ok)
    print(f"OpenWA done: {success}/{len(results)} sent.", flush=True)
    return results


def login_whatsapp():
    print(f"OpenWA session is managed via the API at {OPENWA_URL}")
    print("If disconnected, regenerate the QR via the OpenWA session endpoint.")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        img = sys.argv[1]
        phone = sys.argv[2] if len(sys.argv) > 2 else "+919884063814"
        caption = sys.argv[3] if len(sys.argv) > 3 else ""
        print("Session ready:", check_session())
        print("Sent:", send_image(img, phone, caption))
    else:
        print("Session ready:", check_session())
        print("Usage: python send_whatsapp_openwa.py <image> <phone> [caption]")
