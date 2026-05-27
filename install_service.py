"""
Install ReportFlow as a Windows Service for 24/7 operation
Run as Administrator: python install_service.py install
"""
import sys
import os
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
from pathlib import Path

class ReportFlowService(win32serviceutil.ServiceFramework):
    _svc_name_ = "ReportFlowService"
    _svc_display_name_ = "ReportFlow - Power BI to WhatsApp Service"
    _svc_description_ = "Automated Power BI report delivery to WhatsApp - Runs 24/7"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
        self.is_alive = True

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.is_alive = False

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                             servicemanager.PYS_SERVICE_STARTED,
                             (self._svc_name_, ''))
        self.main()

    def main(self):
        # Change to the script directory
        script_dir = Path(__file__).parent
        os.chdir(script_dir)
        
        # Import and run the Flask app
        try:
            servicemanager.LogInfoMsg("Starting ReportFlow Service...")
            
            # Import the main application
            from app import app
            
            # Run Flask in service mode
            app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
            
        except Exception as e:
            servicemanager.LogErrorMsg(f"Service error: {str(e)}")

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(ReportFlowService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(ReportFlowService)