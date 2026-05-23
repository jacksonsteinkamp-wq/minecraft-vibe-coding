import time
import minescript as m
from minescript_plus import mc, Screen, press_key_bind, ClickType
from .config import MINERAL_ITEMS

HOTBAR_CONTAINER_OFFSET = 36

def move_hotbar_to_inventory():
    inv = m.player_inventory()
    to_move = []
    names = []
    for i in inv:
        if i.slot is not None and i.slot <= 8 and i.item:
            if i.item in MINERAL_ITEMS:
                to_move.append(i.slot)
                names.append(i.item.split(":")[-1])
    if not to_move:
        return
    m.echo(f"[INV] Moving {', '.join(names)}")
    press_key_bind("key.inventory", True)
    time.sleep(0.05)
    press_key_bind("key.inventory", False)
    if not Screen.wait_screen(delay=1000):
        return
    screen = mc.screen
    if screen is None:
        return
    container = screen.getMenu()
    for slot in to_move:
        mc.gameMode.handleInventoryMouseClick(
            container.containerId, slot + HOTBAR_CONTAINER_OFFSET, 0, ClickType.QUICK_MOVE, mc.player)
        time.sleep(0.25)
    Screen.close_screen()
