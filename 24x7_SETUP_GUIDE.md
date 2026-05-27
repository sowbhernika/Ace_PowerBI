# 🚀 ReportFlow 24/7 Service Setup

## 🎯 Quick Setup (Run as Administrator)

### **Step 1: Install Windows Service**
```batch
# Run as Administrator
install_dependencies.bat
```
This installs the Windows service that runs ReportFlow 24/7.

### **Step 2: Configure Auto-Start**
```batch
# Run as Administrator
startup_registry.bat
```
This ensures ReportFlow starts automatically when Windows boots.

### **Step 3: Setup Monitoring**
```batch
# Run as Administrator
setup_task_scheduler.bat
```
This creates scheduled tasks to monitor and restart the service if needed.

### **Step 4: Start the Service**
```batch
start_service.bat
```

---

## ✅ **What This Setup Provides**

### **24/7 Operation**
- ✅ Runs as Windows Service (background, no user login required)
- ✅ Auto-starts when Windows boots
- ✅ Survives system reboots
- ✅ Runs even when user is logged out

### **Auto-Recovery**
- ✅ Service monitor checks health every 5 minutes
- ✅ Auto-restarts if service crashes
- ✅ Auto-restarts if API becomes unresponsive
- ✅ Logging of all restart events

### **System Integration**
- ✅ Windows Services integration
- ✅ Task Scheduler integration
- ✅ Event logging
- ✅ Registry startup entries

---

## 🔧 **Service Management Commands**

### **Install Service**
```batch
python install_service.py install
```

### **Start Service**
```batch
python install_service.py start
```

### **Stop Service**
```batch
python install_service.py stop
```

### **Remove Service**
```batch
python install_service.py remove
```

### **Check Status**
```batch
sc query ReportFlowService
```

---

## 📊 **Monitoring & Logs**

### **Service Status**
- Windows Services Console: `services.msc`
- Look for: "ReportFlow - Power BI to WhatsApp Service"

### **Log Files**
- **Service Monitor**: `service_monitor.log`
- **Windows Event Log**: Windows Event Viewer → Windows Logs → System

### **Health Check URLs**
- **API Health**: http://localhost:5000/api/config
- **Web Interface**: http://localhost:5000

---

## 🔄 **Scheduled Tasks**

### **1. ReportFlow Monitor**
- **Frequency**: Every 5 minutes
- **Purpose**: Check service health and restart if needed
- **Command**: `python monitor_service.py`

### **2. ReportFlow Startup**
- **Frequency**: At system startup
- **Purpose**: Start service automatically when Windows boots
- **Command**: `start_service.bat`

---

## 🛠 **Troubleshooting**

### **Service Won't Start**
```batch
# Check Python path
where python

# Reinstall service
python install_service.py remove
python install_service.py install

# Check Windows Event Log
eventvwr.msc
```

### **Monitor Not Working**
```batch
# Check scheduled tasks
schtasks /query /tn "ReportFlow Monitor"

# Run monitor manually
python monitor_service.py
```

### **API Not Responding**
```batch
# Check service status
sc query ReportFlowService

# Check port availability
netstat -an | findstr :5000

# Restart service
python install_service.py restart
```

---

## 📁 **Files Created**

| File | Purpose |
|------|---------|
| `install_service.py` | Windows service implementation |
| `install_dependencies.bat` | Install service dependencies |
| `start_service.bat` | Start the service |
| `startup_registry.bat` | Add to Windows startup |
| `monitor_service.py` | Service health monitor |
| `setup_task_scheduler.bat` | Configure scheduled tasks |
| `service_monitor.log` | Monitor activity log |

---

## 🌐 **Network Access**

### **Local Network**
- Backend: `http://192.168.1.10:5000`
- Available to all devices on network

### **Frontend Configuration**
- Set API URL in cloud frontend to: `http://192.168.1.10:5000`
- Or public IP if port forwarding configured

---

## 🔐 **Security Considerations**

### **Firewall**
- Service runs on port 5000
- Configure Windows Firewall for network access
- Consider VPN for external access

### **Service Account**
- Service runs as SYSTEM account
- Has necessary permissions for file access
- Isolated from user sessions

---

## ✅ **Verification Checklist**

After setup, verify these items:

- [ ] Service shows as "Running" in Services console
- [ ] API responds at http://localhost:5000
- [ ] Scheduled tasks are active in Task Scheduler
- [ ] Monitor log shows regular health checks
- [ ] Service survives system reboot
- [ ] Frontend can connect from other devices

---

## 🚀 **Ready for 24/7 Operation!**

Your ReportFlow system is now configured for:
- ✅ **24/7 uptime** with automatic restart
- ✅ **System boot resilience** 
- ✅ **Crash recovery** with monitoring
- ✅ **Network accessibility** for remote frontend
- ✅ **Professional deployment** as Windows service