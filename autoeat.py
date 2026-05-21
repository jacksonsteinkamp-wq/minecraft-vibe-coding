import time
import threading
import minescript as m
from minescript_plus import mc

STOP = False
ESCAPE_KEY = 256

FOOD_ITEMS = {
    "minecraft:apple", "minecraft:baked_potato", "minecraft:beef",
    "minecraft:bread", "minecraft:carrot", "minecraft:chicken",
    "minecraft:cooked_beef", "minecraft:cooked_chicken",
    "minecraft:cooked_cod", "minecraft:cooked_mutton",
    "minecraft:cooked_porkchop", "minecraft:cooked_rabbit",
    "minecraft:cooked_salmon", "minecraft:golden_carrot",
    "minecraft:mutton", "minecraft:porkchop", "minecraft:potato",
    "minecraft:pumpkin_pie", "minecraft:rabbit", "minecraft:salmon",
}

def watch_esc():
    global STOP
    with m.EventQueue() as eq:
        eq.register_key_listener()
        while not STOP:
            try:
                event = eq.get(timeout=0.2)
                if event.key == ESCAPE_KEY and event.action == 1:
                    STOP = True
                    m.echo("[AUTOEAT] Stopped.")
                    return
            except Exception:
                pass

def run():
    threading.Thread(target=watch_esc, daemon=True).start()
    m.echo("[AUTOEAT] Running. ESC to stop.")

    while not STOP:
        try:
            food = mc.player.getFoodData().getFoodLevel()
        except Exception:
            time.sleep(5)
            continue

        if food <= 10:
            m.echo(f"[AUTOEAT] Food level {food}, looking for food")
            hands = m.player_hand_items()
            offhand = hands.off_hand
            ate = False

            if offhand and offhand.get("item") in FOOD_ITEMS:
                m.echo("[AUTOEAT] Eating from offhand")
                m.player_press_use(True)
                time.sleep(2)
                m.player_press_use(False)
                time.sleep(0.2)
                m.echo("[AUTOEAT] Ate")
                ate = True

            if not ate:
                prev_slot = mc.player.getInventory().selected
                inv = m.player_inventory()
                for i in inv:
                    if i.slot is not None and i.slot <= 8 and i.item in FOOD_ITEMS:
                        if i.slot != prev_slot:
                            m.player_inventory_select_slot(i.slot)
                            time.sleep(0.1)
                        m.player_press_use(True)
                        time.sleep(2)
                        m.player_press_use(False)
                        time.sleep(0.2)
                        if i.slot != prev_slot:
                            m.player_inventory_select_slot(prev_slot)
                        m.echo("[AUTOEAT] Ate")
                        ate = True
                        break

            if not ate:
                m.echo("[AUTOEAT] No food in offhand or hotbar")

        for _ in range(10):
            if STOP:
                return
            time.sleep(1)

if __name__ == "__main__":
    run()
