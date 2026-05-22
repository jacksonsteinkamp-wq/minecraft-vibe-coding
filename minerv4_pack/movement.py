import math
import time
import minescript as m
from .state import check_stop
from .mining import mine_block_at
from .config import JUMP_HOLD, MOVED_THRESHOLD

def try_step_up(dx, dz, x, y, z):
    check_stop()
    fx, fz = x + dx, z + dz
    front_block = m.getblocklist([(fx, y, fz)])[0]
    if front_block == "minecraft:air":
        return True
    for cx, cy, cz, label in [
        (x, y + 1, z, "player head"),
        (x, y + 2, z, "above player"),
        (fx, y + 1, fz, "front head"),
        (fx, y + 2, fz, "above front"),
    ]:
        check_stop()
        block = m.getblocklist([(cx, cy, cz)])[0]
        if block != "minecraft:air":
            m.echo(f"[MOVE] clearing {label}")
            mine_block_at(cx, cy, cz)
    check_stop()
    before = m.player_position()
    m.player_press_jump(True)
    m.player_press_forward(True)
    wait_until = time.time() + JUMP_HOLD
    try:
        while time.time() < wait_until:
            check_stop()
            time.sleep(0.05)
    finally:
        m.player_press_jump(False)
        m.player_press_forward(False)
    time.sleep(0.1)
    check_stop()
    after = m.player_position()
    moved = math.sqrt((after[0]-before[0])**2 + (after[2]-before[2])**2)
    if moved > MOVED_THRESHOLD:
        return True
    m.echo("[MOVE] jump attempt failed")
    return False
