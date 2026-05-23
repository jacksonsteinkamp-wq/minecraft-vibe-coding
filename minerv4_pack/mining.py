import time
import minescript as m
from .state import check_stop
from .tools import select_tool
from .config import MOVE_TIMEOUT, block_id

def mine_block_at(x, y, z):
    block = block_id(m.getblocklist([(x, y, z)])[0])
    if block == "minecraft:air":
        return True
    select_tool(block)
    last_block = block
    m.player_look_at(x + 0.5, y + 0.5, z + 0.5)
    time.sleep(0.1)
    timeout = time.time() + MOVE_TIMEOUT
    last_recheck = time.time()
    while True:
        check_stop()
        if time.time() > timeout:
            m.echo("[MINE] Timed out on block")
            m.player_press_attack(False)
            return False
        b = block_id(m.getblocklist([(x, y, z)])[0])
        if b == "minecraft:air":
            break
        now = time.time()
        if now - last_recheck >= 0.25:
            item = m.player_hand_items().main_hand
            if b != last_block or not item or item.get("item") == "minecraft:air":
                m.player_press_attack(False)
                check_stop()
                select_tool(b)
                last_block = b
                m.player_press_attack(True)
            last_recheck = now
        m.player_press_attack(True)
        time.sleep(0.05)
    m.player_press_attack(False)
    return True
