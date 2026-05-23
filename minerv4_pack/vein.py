import math
import time
import minescript as m
from .state import check_stop
from .mining import mine_block_at
from .config import ORE_BLOCKS, MOVE_HOLD, block_id

MAX_VEIN_BLOCKS = 40

def _adjacent_scan(dx, dz, x, y, z):
    for adx in (-1, 0, 1):
        for ady in (-1, 0, 1):
            for adz in (-1, 0, 1):
                if adx == 0 and ady == 0 and adz == 0:
                    continue
                bx, by, bz = x + adx, y + ady, z + adz
                b = block_id(m.getblocklist([(bx, by, bz)])[0])
                if b in ORE_BLOCKS:
                    return (bx, by, bz)
    return None

def _step_forward(tx, tz):
    m.player_look_at(tx + 0.5, m.player_position()[1], tz + 0.5)
    m.player_press_forward(True)
    try:
        time.sleep(MOVE_HOLD)
    finally:
        m.player_press_forward(False)

def _clear_headroom_and_enter(bx, by, bz):
    above = block_id(m.getblocklist([(bx, by + 1, bz)])[0])
    if above not in ("minecraft:air", "", None):
        m.player_look_at(bx + 0.5, by + 1.5, bz + 0.5)
        mine_block_at(bx, by + 1, bz)
    deadline = time.time() + 1.5
    while time.time() < deadline:
        check_stop()
        cx, _, cz = map(int, map(math.floor, m.player_position()))
        if (cx, cz) == (bx, bz):
            return
        _step_forward(bx, bz)
        time.sleep(0.05)

def _enqueue_neighbors(bx, by, bz, mined, queue, queued):
    for adx, ady, adz in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]:
        nx, ny, nz = bx + adx, by + ady, bz + adz
        if (nx, ny, nz) in mined or (nx, ny, nz) in queued:
            continue
        b = block_id(m.getblocklist([(nx, ny, nz)])[0])
        if b not in ("minecraft:air", "", None):
            queue.append((nx, ny, nz))
            queued.add((nx, ny, nz))

def mine_ores(dx, dz, x, y, z):
    orig_x, orig_y, orig_z = map(int, map(math.floor, m.player_position()))
    first = _adjacent_scan(dx, dz, orig_x, orig_y, orig_z)
    if first is None:
        return orig_x, orig_z
    m.echo(f"[VEIN] Ore found, entering ore mode")
    orig_yaw, _ = m.player_orientation()
    mined = set()
    queue = [first]
    queued = {first}
    while queue and len(mined) < MAX_VEIN_BLOCKS:
        check_stop()
        bx, by, bz = queue.pop(0)
        if (bx, by, bz) in mined:
            continue
        px, py, pz = map(int, map(math.floor, m.player_position()))
        if (bx, bz) != (px, pz):
            _step_forward(bx, bz)
            time.sleep(0.1)
        m.player_look_at(bx + 0.5, by + 0.5, bz + 0.5)
        if not mine_block_at(bx, by, bz):
            continue
        mined.add((bx, by, bz))
        _enqueue_neighbors(bx, by, bz, mined, queue, queued)
        px, py, pz = map(int, map(math.floor, m.player_position()))
        if by == py and (bx, bz) != (px, pz):
            _clear_headroom_and_enter(bx, by, bz)
    if mined:
        # Phase 1: walk to (orig_x, orig_z) with Y correction
        for _ in range(30):
            check_stop()
            cx, cy, cz = map(int, map(math.floor, m.player_position()))
            if (cx, cz) == (orig_x, orig_z):
                break
            if cy > orig_y:
                m.player_press_forward(False)
                time.sleep(0.3)
            elif cy < orig_y:
                m.player_look_at(orig_x + 0.5, m.player_position()[1], orig_z + 0.5)
                m.player_press_jump(True)
                m.player_press_forward(True)
                try:
                    time.sleep(MOVE_HOLD)
                finally:
                    m.player_press_jump(False)
                    m.player_press_forward(False)
            else:
                _step_forward(orig_x, orig_z)
        # Phase 2: ensure correct Y at target XZ
        for _ in range(20):
            check_stop()
            cx, cy, cz = map(int, map(math.floor, m.player_position()))
            if cy == orig_y:
                break
            if cy > orig_y:
                m.player_press_forward(False)
                time.sleep(0.3)
            else:
                m.player_press_jump(True)
                try:
                    time.sleep(0.3)
                finally:
                    m.player_press_jump(False)
                time.sleep(0.1)
        # Phase 3: face original mining direction
        m.player_look_at(orig_x + dx + 0.5, orig_y + 0.5, orig_z + dz + 0.5)
        m.echo(f"[VEIN] Mined {len(mined)} ore, recentered")
    return orig_x, orig_z
