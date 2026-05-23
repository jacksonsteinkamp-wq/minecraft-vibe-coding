import math
import time
import minescript as m
from .state import check_stop
from .mining import mine_block_at
from .config import JUMP_HOLD, MOVED_THRESHOLD, GRAVITY_BLOCKS, block_id

def _clear_gravity_column(x, y, z):
    for cy in range(y, y + 20):
        check_stop()
        block = block_id(m.getblocklist([(x, cy, z)])[0])
        if block == "minecraft:air":
            break
        if block in GRAVITY_BLOCKS:
            m.echo(f"[MOVE] clearing gravel at y={cy}")
            mine_block_at(x, cy, z)

def try_step_up(dx, dz, x, y, z):
    check_stop()
    fx, fz = x + dx, z + dz
    for attempt in range(3):
        for cx, cy, cz, label in [
            (x, y + 1, z, "player head"),
            (x, y + 2, z, "above player"),
            (fx, y - 1, fz, "front step"),
            (fx, y, fz, "front feet"),
            (fx, y + 1, fz, "front head"),
            (fx, y + 2, fz, "above front"),
        ]:
            check_stop()
            block = block_id(m.getblocklist([(cx, cy, cz)])[0])
            if block != "minecraft:air":
                m.echo(f"[MOVE] clearing {label} (attempt {attempt+1})")
                mine_block_at(cx, cy, cz)
        _clear_gravity_column(fx, y + 1, fz)
        _clear_gravity_column(fx, y + 2, fz)
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
    below = block_id(m.getblocklist([(x, y - 1, z)])[0])
    if below != "minecraft:air":
        m.echo("[MOVE] digging below to escape")
        mine_block_at(x, y - 1, z)
    m.echo("[MOVE] step up failed after 3 attempts")
    return False
