import time
import os
import sys
import subprocess
import minescript as m

def send_discord_notification(message):
    """Executes your discord_webhook2.py script with the custom message."""
    try:
        # Locate your webhook script in the same directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        webhook_script_path = os.path.join(script_dir, "discord_webhook2.py")
        
        # Run your script in the background
        subprocess.run(
            [sys.executable, webhook_script_path, message], 
            check=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
    except Exception as e:
        m.echo(f"❌ Failed to trigger discord_webhook2.py: {e}")

def main():
    m.echo("👀 Crouch Detector Script Activated!")
    m.echo("Press your crouch key (default: Left Shift) to test the Discord link.")
    
    # State tracker to prevent webhook spam
    was_sneaking = False
    
    try:
        while True:
            # Minescript client-side environment check
            is_sneaking = m.get_player_is_sneaking()
            
            # CONDITION: Player just started crouching this frame
            if is_sneaking and not was_sneaking:
                m.echo("📥 Crouch detected! Sending alert...")
                send_discord_notification("📥 Test Notification: The player just crouched in-game!")
                
            # Update the state for the next loop check
            was_sneaking = is_sneaking
            
            # Check 10 times a second to stay responsive without melting your CPU
            time.sleep(0.1)
            
    except Exception as e:
        m.echo(f"🛑 Crouch test loop encountered an error: {e}")

if __name__ == "__main__":
    main()