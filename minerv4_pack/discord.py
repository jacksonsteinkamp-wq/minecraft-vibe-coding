import os
import subprocess
from .config import python_path, SCRIPT_DIR

def discord_ping(msg):
    try:
        webhook = os.path.join(SCRIPT_DIR, "discord_webhook2.py")
        subprocess.Popen([python_path, webhook, msg])
    except Exception:
        pass
