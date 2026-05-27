"""
Monitor OpenWA Docker container and restart if needed.
Add this to your existing service monitor.
"""
import subprocess
import time
import logging

def check_docker_running():
    """Check if Docker Desktop is running."""
    try:
        result = subprocess.run(['docker', 'version'], capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except Exception:
        return False

def check_openwa_container():
    """Check if OpenWA container is running."""
    try:
        result = subprocess.run(['docker', 'ps', '--filter', 'name=openwa-api', '--format', '{{.Status}}'], 
                              capture_output=True, text=True, timeout=10)
        return 'Up' in result.stdout
    except Exception:
        return False

def start_openwa_container():
    """Start the OpenWA container."""
    try:
        logging.info("Starting OpenWA Docker container...")
        
        # Stop existing container
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
        
        if result.returncode == 0:
            logging.info("OpenWA container started successfully")
            return True
        else:
            logging.error(f"Failed to start OpenWA: {result.stderr}")
            return False
    except Exception as e:
        logging.error(f"Error starting OpenWA: {str(e)}")
        return False

def monitor_openwa():
    """Main monitoring function for OpenWA."""
    if not check_docker_running():
        logging.warning("Docker Desktop is not running")
        return False
    
    if not check_openwa_container():
        logging.warning("OpenWA container not running - attempting restart")
        if start_openwa_container():
            logging.info("OpenWA container successfully restarted")
            return True
        else:
            logging.error("Failed to restart OpenWA container")
            return False
    else:
        logging.info("OpenWA container is running properly")
        return True

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        filename='openwa_monitor.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    monitor_openwa()