import math
import time
import minescript as m
from .state import check_stop
from .mining import mine_block_at
from .config import GRAVITY_BLOCKS, JUMP_HOLD, MOVE_HOLD, STUCK_THRESHOLD, block_id
from .eat import auto_eat

MAX_GRAVEL_ITER = 60
CLEAR_ABOVE = 15

def _scan_gravel_stacks(fx, y, fz):
    for cy in range(y + 1, y + CLEAR_ABOVE + 1):
        b = block_id(m.getblocklist([(fx, cy, fz)])[0])
        if b != "minecraft:air" and b not in GRAVITY_BLOCKS:
            return
        if b in GRAVITY_BLOCKS:
            mine_block_at(fx, cy, fz)

def _descend_to_y(target_y):
    for _ in range(20):
        pos = m.player_position()
        cy = int(math.floor(pos[1]))
        cx, cz = int(math.floor(pos[0])), int(math.floor(pos[2]))
        if cy <= target_y:
            break
        below = block_id(m.getblocklist([(cx, cy - 1, cz)])[0])
        if below == "minecraft:air":
            break
        mine_block_at(cx, cy - 1, cz)
        time.sleep(0.3)

def handle_gravel(dx, dz, x, y, z):
    original_y = int(m.player_position()[1])
    m.echo(f"[GRAVEL] Entering gravel mode (y={original_y})")
    fx, fz = x + dx, z + dz
    m.player_press_forward(True)
    try:
        for _ in range(MAX_GRAVEL_ITER):
            check_stop()
            fx, fz = x + dx, z + dz
            try:
                b_head = block_id(m.getblocklist([(fx, y + 1, fz)])[0])
                b_feet = block_id(m.getblocklist([(fx, y, fz)])[0])

                if b_head != "minecraft:air":
                    mine_block_at(fx, y + 1, fz)
                    if b_head in GRAVITY_BLOCKS:
                        _scan_gravel_stacks(fx, y, fz)

                if b_feet != "minecraft:air":
                    mine_block_at(fx, y, fz)

                b_head = block_id(m.getblocklist([(fx, y + 1, fz)])[0])
                b_feet = block_id(m.getblocklist([(fx, y, fz)])[0])

                if b_head == "minecraft:air" and b_feet == "minecraft:air":
                    m.echo("[GRAVEL] Clear, descending and exiting")
                    time.sleep(0.3)
                    _descend_to_y(original_y)
                    return fx, fz, original_y

                for _ in range(3):
                    b_h = block_id(m.getblocklist([(fx, y + 1, fz)])[0])
                    b_f = block_id(m.getblocklist([(fx, y, fz)])[0])
                    if b_h != "minecraft:air":
                        mine_block_at(fx, y + 1, fz)
                        if b_h in GRAVITY_BLOCKS:
                            _scan_gravel_stacks(fx, y, fz)
                    if b_f != "minecraft:air":
                        mine_block_at(fx, y, fz)
                    if block_id(m.getblocklist([(fx, y + 1, fz)])[0]) == "minecraft:air" and block_id(m.getblocklist([(fx, y, fz)])[0]) == "minecraft:air":
                        time.sleep(0.3)
                        break
                    check_stop()
                    time.sleep(0.1)

                x, z = fx, fz
                auto_eat()
            except Exception:
                m.echo("[GRAVEL] Block lookup failed, exiting gravel mode")
                _descend_to_y(original_y)
                return fx, fz, original_y
    finally:
        m.player_press_forward(False)

    m.echo("[GRAVEL] Max iterations reached")
    _descend_to_y(original_y)
    return fx, fz, original_y
