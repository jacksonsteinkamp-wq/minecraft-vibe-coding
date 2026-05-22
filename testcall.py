import subprocess, sys, os
script_dir = os.path.dirname(os.path.abspath(__file__))
subprocess.run([sys.executable, os.path.join(script_dir, "discord_webhook2.py"), "🔗 Pipeline Test: Hello from inside Minecraft!"])