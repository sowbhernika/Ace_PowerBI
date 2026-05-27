# 🐳 Docker + OpenWA 24/7 Setup

## 🚀 **Complete 24/7 Setup for Docker & WhatsApp**

### **Step 1: Start OpenWA Docker Container**
```batch
start_openwa_docker.bat
```
This will:
- ✅ Start OpenWA container with auto-restart
- ✅ Configure for 24/7 operation
- ✅ Set up persistent data storage

### **Step 2: Verify Docker Auto-Start**
1. **Docker Desktop Settings**:
   - Open Docker Desktop
   - Settings → General
   - ✅ Enable "Start Docker Desktop when you log in"

2. **Windows Startup**:
   - Docker will start automatically with Windows
   - OpenWA container has `--restart=always` flag

### **Step 3: Enhanced Monitoring**
Your service monitor now checks:
- ✅ ReportFlow Windows Service
- ✅ Backend API health
- ✅ OpenWA Docker container
- ✅ Auto-restart for all components

---

## 🔧 **Manual Commands**

### **Start OpenWA Container**
```batch
docker run -d --name openwa-api --restart=always -p 2785:2785 -e API_KEY=dev-admin-key -v openwa_data:/app/data open-wa/wa-automate:latest
```

### **Check Container Status**
```batch
docker ps | findstr openwa-api
```

### **View Container Logs**
```batch
docker logs openwa-api
```

### **Restart Container**
```batch
docker restart openwa-api
```

### **Stop Container**
```batch
docker stop openwa-api
```

---

## 📊 **24/7 Operation Summary**

### **What Runs Automatically:**
1. **Windows Service**: ReportFlow backend (port 5000)
2. **Docker Container**: OpenWA WhatsApp API (port 2785)  
3. **Service Monitor**: Checks both every 5 minutes
4. **Auto-Recovery**: Restarts failed components

### **Startup Sequence:**
1. **Windows boots** → Docker Desktop starts
2. **Docker starts** → OpenWA container auto-starts  
3. **Windows Service** starts → ReportFlow backend starts
4. **Task Scheduler** → Service monitor runs every 5 minutes

### **Monitoring & Logs:**
- **Service Monitor**: `service_monitor.log`
- **OpenWA Monitor**: `openwa_monitor.log` 
- **Docker Logs**: `docker logs openwa-api`

---

## 🌐 **Access URLs**

- **Backend API**: http://localhost:5000
- **OpenWA API**: http://localhost:2785
- **Frontend**: http://localhost:8080 (if running)

---

## ✅ **Verification Checklist**

After setup, verify:
- [ ] Docker Desktop starts with Windows
- [ ] OpenWA container shows as "Up" in `docker ps`
- [ ] Backend API responds at localhost:5000
- [ ] OpenWA API responds at localhost:2785
- [ ] Service monitor logs show healthy status
- [ ] WhatsApp QR code appears in frontend Setup tab

---

## 🛠 **Troubleshooting**

### **Container Won't Start**
```batch
# Check Docker is running
docker version

# Try different image
docker run -d --name openwa-api --restart=always -p 2785:2785 smashah/open-wa:latest
```

### **QR Code Not Showing**
1. Check OpenWA container: `docker ps`
2. Check backend API: `curl localhost:5000/api/connections`
3. Check OpenWA API: `curl localhost:2785/api/health`

### **Monitor Not Working**
```batch
# Test monitor manually
python monitor_service.py

# Check scheduled task
schtasks /query /tn "ReportFlow Monitor"
```

---

## 🎯 **Result: Complete 24/7 Operation**

✅ **ReportFlow Backend**: Windows Service (24/7)  
✅ **OpenWA WhatsApp**: Docker Container (24/7)  
✅ **Monitoring**: Auto-restart for both (every 5 min)  
✅ **Boot Resilience**: Starts with Windows  
✅ **Crash Recovery**: Automatic restart on failure  