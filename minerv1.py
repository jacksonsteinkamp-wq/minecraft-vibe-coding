import time
import math
import os
import sys
import subprocess
import minescript as m

def send_discord_notification(reason):
    """
    Finds your discord_webhook2.py script in the same folder 
    and executes it with the shutdown reason as an argument.
    """
    try:
        # Get the folder directory where this miner script lives
        script_dir = os.path.dirname(os.path.abspath(__file__))
        webhook_script_path = os.path.join(script_dir, "discord_webhook2.py")
        
        m.echo("Sending Discord notification via discord_webhook2.py...")
        
        # Run your script exactly how it expects to be run
        subprocess.run(
            [sys.executable, webhook_script_path, reason], 
            check=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
    except Exception as e:
        m.echo(f"❌ Failed to trigger discord_webhook2.py: {e}")

def get_snapped_direction():
    """Reads sloppy angle and returns exact X/Z step vectors for the nearest 90-degree axis."""
    yaw = m.get_player_rotation()[0]
    norm_yaw = yaw % 360
    if norm_yaw < 0: 
        norm_yaw += 360
        
    if 315 <= norm_yaw or norm_yaw < 45:
        return 0, 1   # South (+Z)
    elif 45 <= norm_yaw < 135:
        return -1, 0  # West (-X)
    elif 135 <= norm_yaw < 225:
        return 0, -1  # North (-Z)
    else:
        return 1, 0   # East (+X)

def align_player_camera(dx, dz):
    """Forces the crosshairs to snap perfectly flat and along the design grid."""
    pos = m.get_player_pos()
    px, py, pz = pos[0], pos[1], pos[2]
    
    target_x = px + (dx * 5)
    target_y = py + 1.62
    target_z = pz + (dz * 5)
    
    m.player_look_at(target_x, target_y, target_z)
    time.sleep(0.15) 

def mine_block_at(x, y, z):
    """Aims and mines a block until it becomes air."""
    m.player_look_at(x + 0.5, y + 0.5, z + 0.5)
    time.sleep(0.05)
    
    timeout = time.time() + 10 
    while m.getblock(x, y, z) != "minecraft:air":
        if time.time() > timeout:
            raise Exception("Block took too long to break. Pickaxe is likely broken!")
        m.player_press_attack(True)
        time.sleep(0.05)
    m.player_press_attack(False)

def main():
    m.echo("🚀 Starting Auto-Aligning Miner...")
    stop_reason = "⛏️ Automated mining run completed successfully!"
    
    try:
        dx, dz = get_snapped_direction()
        align_player_camera(dx, dz)
        
        start_pos = m.get_player_pos()
        current_x = int(math.floor(start_pos[0]))
        current_y = int(math.floor(start_pos[1]))
        current_z = int(math.floor(start_pos[2]))
        
        # Test run of 20 blocks
        for step in range(20):
            # Periodic auto-aim realignment every 3 blocks
            if step > 0 and step % 3 == 0:
                align_player_camera(dx, dz)
            
            m.echo(f"Digging step {step + 1}/20...")
            
            tx = current_x + dx
            tz = current_z + dz
            
            # Mine 1x2 tunnel layout
            mine_block_at(tx, current_y + 1, tz)
            mine_block_at(tx, current_y, tz)
            
            # Step forward
            m.player_press_forward(True)
            time.sleep(0.45) 
            m.player_press_forward(False)
            time.sleep(0.05)
            
            current_x = tx
            current_z = tz
            
    except Exception as e:
        stop_reason = f"🚨 Bot stopped due to an error: {str(e)}"
        m.echo(f"🛑 Error detected: {str(e)}")
        raise e
        
    finally:
        m.echo("🔌 Shutting down bot script...")
        # This guarantees your discord_webhook2.py gets executed no matter what
        send_discord_notification(stop_reason)

if __name__ == "__main__":
    main()