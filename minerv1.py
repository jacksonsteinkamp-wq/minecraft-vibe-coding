# minerv1: Basic auto-miner. Straight-line tunnel. Fortune pick on slot 9. Hardcoded +X direction. Discord ping on stop.
import time
import math
import os
import sys
import subprocess
import minescript as m

global python_path
python_path = r"C:\Python314\python.exe"

def call_discord_webhook(message_text):
    #m.echo(f"DEBUG: webhook called with: {message_text}")
    result = subprocess.Popen(
        [python_path, r"C:\Users\jackn\AppData\Roaming\.minecraft\minescript\discord_webhook2.py", message_text],
        #timeout=10
    )
    m.echo(f"returncode: {result.returncode}")

def get_snapped_direction():
    yaw, pitch = m.player_orientation()
    norm_yaw = yaw % 360
    if norm_yaw < 0:
        norm_yaw += 360

    if 315 <= norm_yaw or norm_yaw < 45:
        return 0, 1, "SOUTH (+Z)"
    elif 45 <= norm_yaw < 135:
        return -1, 0, "WEST (-X)"
    elif 135 <= norm_yaw < 225:
        return 0, -1, "NORTH (-Z)"
    else:
        return 1, 0, "EAST (+X)"

def align_player_camera(dx, dz):
    pos = m.player_position()  # FIXED: was m.get_player_pos()
    px, py, pz = pos[0], pos[1], pos[2]
    target_x = px + (dx * 5)
    target_y = py + 1.62
    target_z = pz + (dz * 5)
    m.player_look_at(target_x, target_y, target_z)
    time.sleep(0.15)

def mine_block_at(x, y, z):
    m.player_look_at(x + 0.5, y + 0.5, z + 0.5)
    time.sleep(0.05)

    timeout = time.time() + 10
    while m.getblocklist([(x, y, z)])[0] != "minecraft:air":  # FIXED: was m.getblock()
        if time.time() > timeout:
            raise Exception("Block took too long to break! Is your tool broken?")
        m.player_press_attack(True)
        time.sleep(0.05)
    m.player_press_attack(False)

def main():
    m.echo("⛏️ Initializing Auto-Miner...")
    stop_reason = "Mining done"

    try:
        dx, dz, dir_name = get_snapped_direction()
        m.echo(f"🔒 Direction locked: {dir_name}. Snapping camera...")
        align_player_camera(dx, dz)

        pos = m.player_position()  # FIXED
        current_x = int(math.floor(pos[0]))
        current_y = int(math.floor(pos[1]))
        current_z = int(math.floor(pos[2]))

        for step in range(20):
            if step > 0 and step % 3 == 0:
                align_player_camera(dx, dz)

            m.echo(f"Digging step {step + 1}/20...")

            tx = current_x + dx
            tz = current_z + dz

            mine_block_at(tx, current_y + 1, tz)
            mine_block_at(tx, current_y, tz)

            m.player_press_forward(True)
            time.sleep(0.45)
            m.player_press_forward(False)
            time.sleep(0.05)

            current_x = tx
            current_z = tz

    except Exception as e:
        stop_reason = f"🚨 Bot stopped: {str(e)}"
        m.echo(f"🛑 Mining loop broke: {str(e)}")

    finally:
        m.echo("🔌 Triggering Discord notification...")
        call_discord_webhook(stop_reason)

if __name__ == "__main__":
    main()