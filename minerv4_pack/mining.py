import time
import minescript as m
from .state import check_stop
from .tools import select_tool
from .config import MOVE_TIMEOUT

def mine_block_at(x, y, z):
    block = m.getblocklist([(x, y, z)])[0]
    if block == "minecraft:air":
        return True
    select_tool(block)
    m.player_look_at(x + 0.5, y + 0.5, z + 0.5)
    time.sleep(0.1)
    timeout = time.time() + MOVE_TIMEOUT
    while m.getblocklist([(x, y, z)])[0] != "minecraft:air":
        check_stop()
        if time.time() > timeout:
            m.echo("[MINE] Timed out on block, trying to step up")
            return False
        m.player_press_attack(True)
        time.sleep(0.05)
    m.player_press_attack(False)
    return True
