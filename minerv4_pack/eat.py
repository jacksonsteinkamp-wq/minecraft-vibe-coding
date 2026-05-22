import time
import minescript as m
from minescript_plus import mc
from .config import FOOD_ITEMS, FOOD_THRESHOLD
from .state import check_stop

def _eat_slot():
    m.player_press_use(True)
    try:
        wait_until = time.time() + 2
        while time.time() < wait_until:
            check_stop()
            time.sleep(0.05)
    finally:
        m.player_press_use(False)
    time.sleep(0.2)

def auto_eat():
    try:
        food_level = mc.player.getFoodData().getFoodLevel()
    except Exception:
        return
    if food_level > FOOD_THRESHOLD:
        return
    m.echo(f"[EAT] Food level {food_level}, looking for food")
    hands = m.player_hand_items()
    offhand = hands.off_hand
    if offhand and offhand.get("item") in FOOD_ITEMS:
        _eat_slot()
        m.echo("[EAT] Ate from offhand")
        return
    prev_slot = mc.player.getInventory().selected
    inv = m.player_inventory()
    for i in inv:
        if i.slot is not None and i.slot <= 8 and i.item in FOOD_ITEMS:
            if i.slot != prev_slot:
                m.player_inventory_select_slot(i.slot)
                time.sleep(0.1)
            _eat_slot()
            if i.slot != prev_slot:
                m.player_inventory_select_slot(prev_slot)
            m.echo("[EAT] Ate")
            return
    m.echo("[EAT] No food in offhand or hotbar")
