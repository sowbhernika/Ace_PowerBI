"""
WhatsApp sender using WAHA (WhatsApp HTTP API).
Replaces the Selenium-based sender.
"""

import os
import base64
import time
import requests
from pathlib import Path

WAHA_URL = "http://139.59.24.210"
WAHA_API_KEY = "30e7923b2dfb49b5b768887b197b187b"
WAHA_SESSION = "default"

HEADERS = {"X-Api-Key": WAHA_API_KEY, "Content-Type": "application/json"}


def _chat_id(phone):
    """Convert +919884063814 → 919884063814@c.us"""
    clean = phone.replace("+", "").replace(" ", "").replace("-", "")
    return f"{clean}@c.us"


def check_session():
    """Check if WAHA session is logged in."""
    try:
        r = requests.get(f"{WAHA_URL}/api/sessions",
                         headers={"X-Api-Key": WAHA_API_KEY}, timeout=10)
        for s in r.json():
            if s["name"] == WAHA_SESSION:
                return s["status"] == "WORKING"
    except Exception as e:
        print(f"WAHA session check failed: {e}")
    return False


def send_image(image_path, phone=None, caption=""):
    """Send one image to one phone via WAHA."""
    if not phone:
        print("ERROR: no phone provided")
        return False

    image_path = os.path.abspath(image_path)
    if not os.path.exists(image_path):
        print(f"ERROR: Image not found: {image_path}")
        return False

    # Encode image as base64
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()

    filename = os.path.basename(image_path)
    chat_id = _chat_id(phone)

    payload = {
        "session": WAHA_SESSION,
        "chatId": chat_id,
        "file": {
            "mimetype": "image/png",
            "filename": filename,
            "data": b64,
        },
        "caption": caption or "",
    }

    try:
        r = requests.post(f"{WAHA_URL}/api/sendImage",
                          headers=HEADERS, json=payload, timeout=60)
        if r.status_code == 200 or r.status_code == 201:
            print(f"  Sent to {phone}")
            return True
        else:
            print(f"  Failed {phone}: HTTP {r.status_code} - {r.text[:150]}")
            return False
    except Exception as e:
        print(f"  Failed {phone}: {e}")
        return False


def send_batch(jobs):
    """Send multiple images via WAHA API.

    jobs: list of (image_path, phone, caption) tuples
    Returns: list of (phone, success) tuples
    """
    if not jobs:
        return []

    print(f"WAHA batch: {len(jobs)} message(s)...")

    if not check_session():
        print("ERROR: WAHA session is not WORKING. Check the dashboard.")
        return [(j[1], False) for j in jobs]

    results = []
    for i, (image_path, phone, caption) in enumerate(jobs):
        print(f"  [{i+1}/{len(jobs)}] -> {phone}")
        ok = send_image(image_path, phone, caption)
        results.append((phone, ok))
        # Small delay between messages
        if i < len(jobs) - 1:
            time.sleep(2)

    success = sum(1 for _, ok in results if ok)
    print(f"WAHA done: {success}/{len(results)} sent.")
    return results


# Compat aliases (so existing code keeps working)
def login_whatsapp():
    print(f"WAHA session is managed on the server: {WAHA_URL}/dashboard/")
    print("Login QR is shown there. Nothing to do locally.")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        img = sys.argv[1]
        phone = sys.argv[2] if len(sys.argv) > 2 else "+919884063814"
        caption = sys.argv[3] if len(sys.argv) > 3 else ""
        send_image(img, phone, caption)
    else:
        print("Usage: python send_whatsapp_waha.py <image> <phone> [caption]")
        print(f"Session WORKING: {check_session()}")
