# Ace Power BI WhatsApp Manager

Automated tool that takes screenshots of Power BI dashboard reports and sends them via WhatsApp on a schedule.

## Setup

1. **Create virtual environment**
   ```
   python -m venv venv
   venv\Scripts\activate
   pip install flask selenium
   ```

2. **Login to Power BI** (one-time, opens browser for MFA)
   ```
   login_powerbi.bat
   ```

3. **Login to WhatsApp** (one-time, scan QR with phone)
   ```
   login_whatsapp_selenium.bat
   ```

4. **Run the web UI**
   ```
   python app.py
   ```
   Open http://localhost:5000

## Files

- `app.py` — Flask web UI server
- `powerbi_whatsapp.py` — Screenshot + filter logic
- `send_whatsapp_selenium.py` — WhatsApp sending via Selenium
- `config.json` — Report list, recipients, schedule
- `templates/index.html` — Dashboard UI

## Features

- Select reports from a thumbnail grid
- Dynamic filters that adjust to today's date automatically
  - Material Matching: current week + next 2 weeks
  - Baywise Output: month-start → today
  - Ontime Delivery: per-plant filter (AMC/APE/AHF)
- Add/remove WhatsApp recipients
- Schedule daily / weekday / specific days / one-time sends
- Windows Task Scheduler integration
