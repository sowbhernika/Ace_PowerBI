"""
WhatsApp sender via the local OpenWA Node gateway (whatsapp-web.js, no Docker).
Gateway: whatsapp-gateway/openwa-server.js  (run on port 2786)

Endpoints used:
  GET  /api/status       -> {authenticated, status, has_qr}
  GET  /api/qr           -> {qr, status} | {authenticated:true}
  POST /api/relink       -> reinitialize (fresh QR)
  POST /api/send-image   -> {number, image(base64), caption, filename}
"""

import os
import base64
import time
import requests

GATEWAY_URL = "http://localhost:2786"
READY_STATES = ("authenticated", "ready", "connected")

# Back-compat aliases (other modules import these names)
OPENWA_URL = GATEWAY_URL
OPENWA_API_KEY = ""
OPENWA_SESSION_ID = "reportflow"
OPENWA_CONTAINER = ""


def _status():
    try:
        r = requests.get(f"{GATEWAY_URL}/api/status", timeout=8)
        return r.json()
    except Exception:
        return {}


def check_session():
    """True if the gateway WhatsApp client is authenticated."""
    s = _status()
    return bool(s.get("authenticated")) or s.get("status") in READY_STATES


def ensure_session_ready(max_wait=60):
    """Wait for the gateway to be authenticated. whatsapp-web.js auto-restores
    a saved login on startup, so this just waits; it cannot scan a QR for you."""
    if check_session():
        return True
    print("WhatsApp not authenticated yet — waiting for the gateway to restore session…", flush=True)
    waited = 0
    while waited < max_wait:
        if check_session():
            print("WhatsApp connected.", flush=True)
            return True
        time.sleep(4)
        waited += 4
    print("ERROR: WhatsApp not connected. Open the dashboard → WhatsApp tab and Link with QR.", flush=True)
    return False


def get_qr():
    """Return a QR data-URL for linking, or None if already connected."""
    try:
        r = requests.get(f"{GATEWAY_URL}/api/qr", timeout=8).json()
        if r.get("authenticated"):
            return None
        return r.get("qr")
    except Exception:
        return None


def relink():
    """Log out and reinitialize so a fresh QR is produced (for a new number)."""
    try:
        requests.post(f"{GATEWAY_URL}/api/relink", timeout=10)
        return True
    except Exception:
        return False


def send_image(image_path, phone=None, caption=""):
    """Send one image to one phone via the gateway."""
    if not phone:
        print("ERROR: no phone provided"); return False
    image_path = os.path.abspath(image_path)
    if not os.path.exists(image_path):
        print(f"ERROR: image not found: {image_path}"); return False

    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    number = phone.replace("+", "").replace(" ", "").replace("-", "")
    payload = {"number": number, "image": b64,
               "filename": os.path.basename(image_path), "caption": caption or ""}
    try:
        r = requests.post(f"{GATEWAY_URL}/api/send-image", json=payload, timeout=90)
        if r.status_code == 200 and r.json().get("success"):
            return True
        print(f"  Failed {phone}: HTTP {r.status_code} - {r.text[:150]}")
        return False
    except Exception as e:
        print(f"  Failed {phone}: {e}")
        return False


def send_batch(jobs):
    """Send many (image_path, phone, caption) jobs. Returns [(phone, ok)]."""
    if not jobs:
        return []
    print(f"Gateway batch: {len(jobs)} message(s)…", flush=True)
    if not ensure_session_ready():
        return [(j[1], False) for j in jobs]

    results = []
    for i, (image_path, phone, caption) in enumerate(jobs):
        ok = send_image(image_path, phone, caption)
        print(f"  [{i+1}/{len(jobs)}] {'sent' if ok else 'FAILED'} -> {phone}", flush=True)
        results.append((phone, ok))
        if i < len(jobs) - 1:
            time.sleep(2)
    print(f"Gateway done: {sum(1 for _,ok in results if ok)}/{len(results)} sent.", flush=True)
    return results


def login_whatsapp():
    print(f"WhatsApp is managed by the gateway at {GATEWAY_URL}. "
          f"Use the dashboard → WhatsApp tab to scan the QR.")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        img = sys.argv[1]
        phone = sys.argv[2] if len(sys.argv) > 2 else "+919884063814"
        cap = sys.argv[3] if len(sys.argv) > 3 else ""
        print("Connected:", check_session())
        print("Sent:", send_image(img, phone, cap))
    else:
        print("Connected:", check_session())
        print("Usage: python send_whatsapp_openwa.py <image> <phone> [caption]")
