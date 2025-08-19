import json
import os
import sys
import subprocess
from pathlib import Path

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(PROJECT_DIR, 'config', 'config.json')
WEB_INTERFACE_SCRIPT = os.path.join(PROJECT_DIR, 'web_interface_v2.py')

def install_dependencies():
    """Install required dependencies using system Python."""
    print("Installing dependencies...")
    try:
        requirements_file = os.path.join(PROJECT_DIR, 'requirements_web_v2.txt')
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', '--break-system-packages', '-r', requirements_file
        ])
        print("Dependencies installed successfully")
        
        # Install rgbmatrix module from local source
        print("Installing rgbmatrix module...")
        rgbmatrix_path = Path(PROJECT_DIR) / 'rpi-rgb-led-matrix-master' / 'bindings' / 'python'
        if rgbmatrix_path.exists():
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', '--break-system-packages', '-e', str(rgbmatrix_path)
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("rgbmatrix module installed successfully")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {e}")
        return False

def main():
    try:
        with open(CONFIG_FILE, 'r') as f:
            config_data = json.load(f)
    except FileNotFoundError:
        print(f"Config file {CONFIG_FILE} not found. Web interface will not start.")
        sys.exit(0) # Exit gracefully, don't start
    except Exception as e:
        print(f"Error reading config file {CONFIG_FILE}: {e}. Web interface will not start.")
        sys.exit(1) # Exit with error, service might restart depending on config

    autostart_enabled = config_data.get("web_display_autostart", False)

    if autostart_enabled is True: # Explicitly check for True
        print("Configuration 'web_display_autostart' is true. Starting web interface...")
        
        # Install dependencies
        if not install_dependencies():
            print("Failed to install dependencies. Exiting.")
            sys.exit(1)
        
        try:
            # Replace the current process with web_interface.py using system Python
            # This is important for systemd to correctly manage the web server process.
            # Ensure PYTHONPATH is set correctly if web_interface.py has relative imports to src
            # The WorkingDirectory in systemd service should handle this for web_interface.py
            print(f"Launching web interface: {sys.executable} {WEB_INTERFACE_SCRIPT} (USE_THREADING={os.getenv('USE_THREADING','0')}, FORCE_THREADING={os.getenv('FORCE_THREADING','0')})")
            os.execvp(sys.executable, [sys.executable, WEB_INTERFACE_SCRIPT])
        except Exception as e:
            print(f"Failed to exec web interface: {e}")
            sys.exit(1) # Failed to start
    else:
        print("Configuration 'web_display_autostart' is false or not set. Web interface will not be started.")
        sys.exit(0) # Exit gracefully, service considered successful

if __name__ == '__main__':
    main() 