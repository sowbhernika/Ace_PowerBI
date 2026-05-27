"""
Monitor and auto-restart ReportFlow service if it fails
Run this as a scheduled task every 5 minutes
"""
import subprocess
import time
import logging
from datetime import datetime
import requests

# Setup logging
logging.basicConfig(
    filename='service_monitor.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def check_service_status():
    """Check if the ReportFlow service is running"""
    try:
        result = subprocess.run(['sc', 'query', 'ReportFlowService'], 
                              capture_output=True, text=True)
        return 'RUNNING' in result.stdout
    except Exception as e:
        logging.error(f"Failed to check service status: {e}")
        return False

def check_api_health():
    """Check if the API is responding"""
    try:
        response = requests.get('http://localhost:5000/api/config', timeout=10)
        return response.status_code == 200
    except Exception as e:
        logging.warning(f"API health check failed: {e}")
        return False

def restart_service():
    """Restart the ReportFlow service"""
    try:
        logging.info("Attempting to restart ReportFlow service...")
        
        # Stop service
        subprocess.run(['python', 'install_service.py', 'stop'], check=True)
        time.sleep(5)
        
        # Start service
        subprocess.run(['python', 'install_service.py', 'start'], check=True)
        time.sleep(10)
        
        logging.info("Service restart completed")
        return True
    except Exception as e:
        logging.error(f"Failed to restart service: {e}")
        return False

def check_openwa_docker():
    """Check if OpenWA Docker container is running"""
    try:
        result = subprocess.run(['docker', 'ps', '--filter', 'name=openwa-api', '--format', '{{.Status}}'], 
                              capture_output=True, text=True, timeout=10)
        return 'Up' in result.stdout
    except Exception as e:
        logging.warning(f"Could not check OpenWA Docker: {e}")
        return False

def restart_openwa_docker():
    """Restart OpenWA Docker container"""
    try:
        logging.info("Restarting OpenWA Docker container...")
        
        # Stop and remove existing
        subprocess.run(['docker', 'stop', 'openwa-api'], capture_output=True, timeout=10)
        subprocess.run(['docker', 'rm', 'openwa-api'], capture_output=True, timeout=10)
        
        # Start new container
        result = subprocess.run([
            'docker', 'run', '-d',
            '--name', 'openwa-api',
            '--restart=always',
            '-p', '2785:2785',
            '-e', 'API_KEY=dev-admin-key',
            '-v', 'openwa_data:/app/data',
            'open-wa/wa-automate:latest'
        ], capture_output=True, text=True, timeout=60)
        
        return result.returncode == 0
    except Exception as e:
        logging.error(f"Failed to restart OpenWA Docker: {e}")
        return False

def main():
    """Main monitoring function"""
    logging.info("Service monitor check started")
    
    service_running = check_service_status()
    api_healthy = check_api_health()
    openwa_running = check_openwa_docker()
    
    # Check and restart main service
    if not service_running:
        logging.warning("Service not running - attempting restart")
        if restart_service():
            logging.info("Service successfully restarted")
        else:
            logging.error("Failed to restart service")
    elif not api_healthy:
        logging.warning("Service running but API not responding - restarting")
        if restart_service():
            logging.info("Service successfully restarted due to API issues")
    else:
        logging.info("Service and API are healthy")
    
    # Check and restart OpenWA Docker
    if not openwa_running:
        logging.warning("OpenWA Docker container not running - attempting restart")
        if restart_openwa_docker():
            logging.info("OpenWA Docker container successfully restarted")
        else:
            logging.error("Failed to restart OpenWA Docker container")
    else:
        logging.info("OpenWA Docker container is healthy")

if __name__ == "__main__":
    main()