import math
import threading
import time
import minescript as m
from . import state
from .config import TRASH_INTERVAL, STUCK_THRESHOLD, MOVE_HOLD, ESCAPE_KEY
from .discord import discord_ping
from .trash import drop_trash
from .eat import auto_eat
from .mining import mine_block_at
from .movement import try_step_up

def watch_for_escape():
    with m.EventQueue() as eq:
        eq.register_key_listener()
        while not state.STOP:
            try:
                event = eq.get(timeout=0.2)
                if event.key == ESCAPE_KEY and event.action == 1:
                    state.STOP = True
                    state.STOP_REASON = "user"
                    m.echo("[ESC] Stopped.")
                    return
            except Exception:
                pass

def get_snapped_direction():
    yaw, _ = m.player_orientation()
    norm_yaw = yaw % 360
    if norm_yaw < 0:
        norm_yaw += 360
    if 315 <= norm_yaw or norm_yaw < 45:
        return 0, 1
    elif 45 <= norm_yaw < 135:
        return -1, 0
    elif 135 <= norm_yaw < 225:
        return 0, -1
    else:
        return 1, 0

def main():
    state.STOP = False
    state.STOP_REASON = None
    threading.Thread(target=watch_for_escape, daemon=True).start()
    dx, dz = get_snapped_direction()
    m.echo(f"Auto miner online. Mining direction: ({dx}, {dz}). ESC to stop.")
    pos = m.player_position()
    x, y, z = map(int, map(math.floor, pos))
    segment = 0
    last_trash = time.time()
    try:
        while True:
            state.check_stop()
            fx, fz = x + dx, z + dz
            ok = mine_block_at(fx, y + 1, fz)
            ok = mine_block_at(fx, y, fz) and ok
            if not ok:
                m.echo("[MOVE] mining failed, trying to step up")
                if not try_step_up(dx, dz, x, y, z):
                    raise Exception("Cannot move forward")
            else:
                before = m.player_position()
                m.player_press_forward(True)
                try:
                    wait_until = time.time() + MOVE_HOLD
                    while time.time() < wait_until:
                        state.check_stop()
                        time.sleep(0.05)
                finally:
                    m.player_press_forward(False)
                after = m.player_position()
                moved = math.sqrt((after[0]-before[0])**2 + (after[2]-before[2])**2)
                if moved < STUCK_THRESHOLD:
                    m.echo("[MOVE] stuck detected")
                    if not try_step_up(dx, dz, x, y, z):
                        raise Exception("Cannot move forward")
            x, z = fx, fz
            segment += 1
            auto_eat()
            now = time.time()
            if now - last_trash >= TRASH_INTERVAL:
                drop_trash(dx, dz)
                last_trash = now
    except Exception as e:
        m.echo(f"[FATAL] {e}")
        if state.STOP_REASON not in ("user", "inventory_full"):
            discord_ping(f"Miner stopped: {e}")
        state.STOP = True

if __name__ == "__main__":
    main()
