python_path = r"C:\Python314\python.exe"
import subprocess, sys, os

result = subprocess.run(
    [python_path, r"C:\Users\jackn\AppData\Roaming\.minecraft\minescript\discord_webhook2.py", "Hello <@1130279768856723596>! This is a test message from minescript."],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)
m.echo(f"returncode: {result.returncode}")
m.echo(f"stderr: {result.stderr.decode()}")