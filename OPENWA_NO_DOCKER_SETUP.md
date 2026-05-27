# OpenWA Setup Without Docker - Alternative WhatsApp Integration

This guide explains how to set up OpenWA (WhatsApp automation) without using Docker, providing multiple WhatsApp integration options for the Power BI to WhatsApp automation system.

## 🚀 Quick Overview

This system now supports **multiple WhatsApp integration methods**:

1. **WhatsApp Web.js** (Port 2786) - Primary method
2. **OpenWA Direct** (Port 2787) - Alternative method  
3. **Switch between services** via the web interface

## 📁 Project Structure

```
Ace_PowerBI/
├── whatsapp-gateway/          # WhatsApp Web.js implementation
│   ├── openwa-server.js      # Main server file
│   └── package.json          # Dependencies
├── openwa-server/             # OpenWA direct implementation
│   ├── simple-server.js      # Simplified OpenWA server
│   ├── patched-openwa-server.js  # Enhanced version
│   └── package.json          # Dependencies
├── templates/index.html       # Web interface with Flow Dashboard
└── app.py                    # Flask backend
```

## 🛠️ Installation Steps

### 1. Prerequisites

- **Node.js 18+** (Download from nodejs.org)
- **Python 3.8+**
- **Chrome/Chromium browser** (for WhatsApp Web automation)

### 2. Install Node.js Dependencies

```bash
# Install WhatsApp Web.js dependencies
cd whatsapp-gateway
npm install whatsapp-web.js express qrcode cors

# Install OpenWA dependencies  
cd ../openwa-server
npm install @open-wa/wa-automate express cors
```

### 3. Install Python Dependencies

```bash
cd ..
pip install flask requests python-dotenv schedule
```

## 🚀 Running the Services

### Method 1: Start All Services

```bash
# Terminal 1: Start Flask backend
python app.py

# Terminal 2: Start WhatsApp Web.js server
cd whatsapp-gateway
node openwa-server.js

# Terminal 3: Start OpenWA server (alternative)
cd openwa-server
node simple-server.js
```

### Method 2: Use Batch Files

Run the included batch files:

```bash
# Start main Flask app
start_service.bat

# Start OpenWA services
setup_openwa_nodejs.bat
```

## 🌐 Access the System

1. **Web Interface**: http://localhost:5000 (or 5002)
2. **Flow Dashboard**: First tab - shows real-time system status
3. **WhatsApp Management**: Dedicated WhatsApp tab for connection management

## 📱 WhatsApp Setup Process

### Option 1: WhatsApp Web.js (Recommended)

1. Go to **WhatsApp tab** in the web interface
2. Click **"Link with QR"** for WhatsApp Web.js
3. Scan QR code with your WhatsApp mobile app:
   - Open WhatsApp → Settings → Linked Devices → Link a Device
4. Wait for "Connected" status

### Option 2: OpenWA Alternative

1. Go to **WhatsApp tab** in the web interface  
2. Click **"Link with QR"** for OpenWA Server
3. Scan QR code with your WhatsApp mobile app
4. Select active service from dropdown

## ⚙️ Service Configuration

### Port Configuration

| Service | Port | Purpose |
|---------|------|---------|
| Flask App | 5000 | Main web interface |
| WhatsApp Web.js | 2786 | Primary WhatsApp service |
| OpenWA Server | 2787 | Alternative WhatsApp service |

### Switching WhatsApp Services

The web interface allows you to switch between WhatsApp services:

1. Go to **WhatsApp tab**
2. Use **"Active Connection"** dropdown
3. Select between:
   - WhatsApp Web.js (Port 2786)
   - OpenWA Server (Port 2787)

## 🎯 Flow Dashboard Features

The new **Flow Dashboard** provides:

- **Real-time Statistics**: Reports enabled, active managers, success rate
- **Service Status**: Power BI and WhatsApp connection monitoring  
- **Quick Actions**: Send reports, manage settings
- **Recent Activity**: Last 5 send attempts with status
- **Professional Interface**: Clean, modern design

## 🔧 Troubleshooting

### WhatsApp Connection Issues

```bash
# Check if services are running
netstat -an | findstr :2786  # WhatsApp Web.js
netstat -an | findstr :2787  # OpenWA Server

# Restart WhatsApp services
cd whatsapp-gateway && node openwa-server.js
cd openwa-server && node simple-server.js
```

### Common Issues

1. **"QR not ready"**: Wait 30 seconds and refresh
2. **"Service not responding"**: Restart the Node.js service
3. **"Authentication failed"**: Use "Relink" button to get fresh QR

### Service Logs

Monitor service logs for debugging:

```bash
# WhatsApp Web.js logs
cd whatsapp-gateway && node openwa-server.js

# OpenWA logs
cd openwa-server && node simple-server.js
```

## 🚀 Production Deployment

### Windows Service Setup

1. Use included batch files for automatic startup:
   ```bash
   setup_task_scheduler.bat
   startup_registry.bat
   ```

2. Or create Windows services:
   ```bash
   python install_service.py
   ```

### Process Monitoring

The system includes monitoring scripts:

- `monitor_service.py` - Monitors Flask app
- `monitor_openwa_docker.py` - Monitors WhatsApp services

## 📊 API Endpoints

### WhatsApp Web.js API (Port 2786)

```bash
GET  /api/health       # Health check
GET  /api/status       # Connection status
GET  /api/qr          # Get QR code
POST /api/send        # Send message
POST /api/relink      # Reconnect WhatsApp
```

### OpenWA API (Port 2787)

```bash
GET  /api/health       # Health check  
GET  /api/status       # Connection status
GET  /api/qr          # Get QR code
POST /api/send        # Send message
POST /api/relink      # Reconnect WhatsApp
```

## ✅ Advantages of No-Docker Setup

- **Faster startup** - No Docker overhead
- **Easier debugging** - Direct access to logs
- **Better resource usage** - Native process execution
- **Simpler deployment** - No Docker dependencies
- **Multiple options** - Both WhatsApp Web.js and OpenWA support

## 🔗 Integration with Power BI

The system automatically:

1. **Generates reports** from Power BI dashboards
2. **Captures thumbnails** for preview
3. **Sends via WhatsApp** to configured managers
4. **Tracks delivery** status and success rates
5. **Provides analytics** via Flow Dashboard

## 📝 Configuration Files

Key configuration is stored in:

- `config.json` - Main application settings
- `profiles/` - WhatsApp session data
- `templates/index.html` - Web interface

## 🆘 Support

For issues:

1. Check **Flow Dashboard** for service status
2. Review **connection logs** in WhatsApp tab
3. Restart services if needed
4. Use **"Relink"** for fresh WhatsApp connection

---

**🎉 You now have a complete Power BI to WhatsApp automation system running without Docker!**

The Flow Dashboard provides full visibility into your automation pipeline, and you can easily switch between different WhatsApp integration methods as needed.