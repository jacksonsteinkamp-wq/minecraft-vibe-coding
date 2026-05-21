# minerv4: v3 + integrated auto-eat (offhand or hotbar, restores selected slot) + fatal error handler (Discord ping on crash, not on ESC/inventory full).
import os
import time
import math
import threading
import subprocess
import minescript as m
import winsound
from minescript_plus import Inventory, mc, Screen, Gui, Key, Client, Player, Server, World, Trading, Hud, Util, Keybind, Event, input

python_path = r"C:\Python314\python.exe"
SCRIPT_DIR = os.path.dirname(__file__)

# ─── GLOBAL STATE ─────────────────────────────────────────────────────────────

STOP = False
STOP_REASON = None
ESCAPE_KEY = 256

# ─── ESC WATCHER ─────────────────────────────────────────────────────────────

def watch_for_escape():
    global STOP
    with m.EventQueue() as eq:
        eq.register_key_listener()
        while not STOP:
            try:
                event = eq.get(timeout=0.2)
                if event.key == ESCAPE_KEY and event.action == 1:
                    STOP = True
                    STOP_REASON = "user"
                    m.echo("[ESC] Stopped.")
                    return
            except Exception:
                pass

def check_stop():
    if STOP:
        if STOP_REASON == "user":
            raise Exception("Stopped by user")
        return

# ─── BLOCK DATA ───────────────────────────────────────────────────────────────

SHOVEL_BLOCKS = {
    "minecraft:dirt", "minecraft:gravel", "minecraft:sand",
    "minecraft:grass_block", "minecraft:coarse_dirt",
    "minecraft:rooted_dirt", "minecraft:mud", "minecraft:clay",
    "minecraft:soul_sand", "minecraft:soul_soil",
}

ORE_BLOCKS = {
    "minecraft:coal_ore", "minecraft:iron_ore", "minecraft:copper_ore",
    "minecraft:gold_ore", "minecraft:redstone_ore", "minecraft:lapis_ore",
    "minecraft:diamond_ore", "minecraft:emerald_ore",
    "minecraft:ancient_debris",
}

PICK_TIER = {
    "minecraft:wooden_pickaxe": 0,
    "minecraft:stone_pickaxe": 1,
    "minecraft:iron_pickaxe": 2,
    "minecraft:diamond_pickaxe": 3,
    "minecraft:netherite_pickaxe": 4,
}

SHOVEL_ITEMS = {
    "minecraft:wooden_shovel", "minecraft:stone_shovel",
    "minecraft:iron_shovel", "minecraft:diamond_shovel",
    "minecraft:netherite_shovel",
}

FOOD_ITEMS = {
    "minecraft:apple",
    "minecraft:baked_potato",
    "minecraft:beef",
    "minecraft:bread",
    "minecraft:carrot",
    "minecraft:chicken",
    "minecraft:cooked_beef",
    "minecraft:cooked_chicken",
    "minecraft:cooked_cod",
    "minecraft:cooked_mutton",
    "minecraft:cooked_porkchop",
    "minecraft:cooked_rabbit",
    "minecraft:cooked_salmon",
    "minecraft:golden_carrot",
    "minecraft:mutton",
    "minecraft:porkchop",
    "minecraft:potato",
    "minecraft:pumpkin_pie",
    "minecraft:rabbit",
    "minecraft:salmon",
}

TRASH_ITEMS = {
    "minecraft:cobblestone",
    "minecraft:cobbled_deepslate",
    "minecraft:dirt",
    "minecraft:gravel",
    "minecraft:andesite",
    "minecraft:diorite",
    "minecraft:granite",
}

# ─── TOOL LOGIC ───────────────────────────────────────────────────────────────

def get_hotbar_tools():
    inv = m.player_inventory()

    picks = []
    shovels = []

    for i in inv:
        if i.slot is None or i.slot > 8:
            continue

        if i.item in PICK_TIER:
            picks.append((i.slot, i))
        elif i.item in SHOVEL_ITEMS:
            shovels.append((i.slot, i))

    return picks, shovels

def best_pick(picks):
    return max(picks, key=lambda x: PICK_TIER.get(x[1].item, -1))

def get_fortune_pick():
    inv = m.player_inventory()

    for i in inv:
        if i.slot == 8 and i.item in PICK_TIER:
            return i.slot, i

    return None

def select_pick(block):
    picks, _ = get_hotbar_tools()
    if not picks:
        raise Exception("No pickaxes")

    is_ore = block in ORE_BLOCKS
    fortune = get_fortune_pick()

    normal_picks = [(s, i) for s, i in picks if s != 8]

    if is_ore and fortune:
        slot, item = fortune

    elif normal_picks:
        slot, item = best_pick(normal_picks)

    elif fortune:
        slot, item = fortune

    else:
        raise Exception("No usable pickaxe")

    m.player_inventory_select_slot(slot)
    time.sleep(0.1)

def select_shovel():
    _, shovels = get_hotbar_tools()
    if not shovels:
        raise Exception("No shovel")

    slot, item = shovels[0]
    m.player_inventory_select_slot(slot)
    time.sleep(0.1)

def select_tool(block):
    if block in SHOVEL_BLOCKS:
        select_shovel()
    else:
        select_pick(block)

# ─── TRASH ────────────────────────────────────────────────────────────────────

def drop_trash(dx, dz):
    global STOP, STOP_REASON
    m.echo("[TRASH] dumping junk")

    pos = m.player_position()

    # turn around
    m.player_look_at(pos[0] - dx * 5, pos[1] + 1.6, pos[2] - dz * 5)
    time.sleep(0.2)

    prev_total = 9999
    while True:
        inv = m.player_inventory()

        hotbar_trash = [i.slot for i in inv if i.slot is not None and i.slot <= 8 and i.item in TRASH_ITEMS]
        if hotbar_trash:
            Inventory.drop_slots(hotbar_trash)

        inv = m.player_inventory()
        main_trash = [i.slot for i in inv if i.slot is not None and 9 <= i.slot <= 35 and i.item in TRASH_ITEMS]
        total_trash = len(hotbar_trash) + len(main_trash)

        if total_trash == 0:
            m.echo("[TRASH] No trash found")
            break

        if total_trash >= prev_total:
            m.echo("[TRASH] No progress — hotbar probably full")
            break
        prev_total = total_trash

        if not main_trash:
            break

        m.echo(f"[TRASH] Shift-clicking {len(main_trash)} items")
        Inventory.move_to_hotbar(main_trash, [])

        inv = m.player_inventory()
        new_hotbar_trash = [i.slot for i in inv if i.slot is not None and i.slot <= 8 and i.item in TRASH_ITEMS]
        if new_hotbar_trash:
            Inventory.drop_slots(new_hotbar_trash)

    # face forward again
    pos = m.player_position()
    m.player_look_at(pos[0] + dx * 5, pos[1] + 1.6, pos[2] + dz * 5)
    time.sleep(0.2)

    inv = m.player_inventory()
    occupied = len([i for i in inv if i.slot is not None and i.slot <= 35])
    if occupied >= 35:
        m.echo("[TRASH] Inventory full, stopping")
        discord_ping("Inventory full! Miner stopped.")
        STOP = True
        STOP_REASON = "inventory_full"

# ─── AUTO-EAT ───────────────────────────────────────────────────────────

def auto_eat():
    try:
        food_level = mc.player.getFoodData().getFoodLevel()
    except Exception:
        return
    if food_level > 10:
        return

    m.echo(f"[EAT] Food level {food_level}, looking for food")

    hands = m.player_hand_items()
    offhand = hands.off_hand
    if offhand and offhand.get("item") in FOOD_ITEMS:
        m.player_press_use(True)
        time.sleep(2)
        m.player_press_use(False)
        time.sleep(0.2)
        m.echo("[EAT] Ate from offhand")
        return

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
            m.echo("[EAT] Ate")
            return

    m.echo("[EAT] No food in offhand or hotbar")

# ─── MOVEMENT RECOVERY ───────────────────────────────────────────────────────

def try_step_up(dx, dz, x, y, z):
    check_stop()
    fx, fz = x + dx, z + dz

    # Check if already unstuck
    front_block = m.getblocklist([(fx, y, fz)])[0]
    if front_block == "minecraft:air":
        return True

    # Clear every block that could block the jump
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

    # One real jump attempt
    check_stop()
    before = m.player_position()
    m.player_press_jump(True)
    m.player_press_forward(True)

    wait_until = time.time() + 0.6
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

    if moved > 0.35:
        return True

    m.echo("[MOVE] jump attempt failed")
    return False

# ─── MINING ───────────────────────────────────────────────────────────────────

def mine_block_at(x, y, z):
    block = m.getblocklist([(x, y, z)])[0]
    if block == "minecraft:air":
        return True

    select_tool(block)

    m.player_look_at(x + 0.5, y + 0.5, z + 0.5)
    time.sleep(0.1)

    timeout = time.time() + 10

    while m.getblocklist([(x, y, z)])[0] != "minecraft:air":
        check_stop()
        if time.time() > timeout:
            m.echo("[MINE] Timed out on block, trying to step up")
            return False

        m.player_press_attack(True)
        time.sleep(0.05)

    m.player_press_attack(False)
    return True

# ─── DISCORD ─────────────────────────────────────────────────────────────

def discord_ping(msg):
    try:
        webhook = os.path.join(SCRIPT_DIR, "discord_webhook2.py")
        subprocess.Popen([python_path, webhook, msg])
    except Exception:
        pass

# ─── DIRECTION ───────────────────────────────────────────────────────────

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

# ─── MAIN LOOP ────────────────────────────────────────────────────────────────

def main():
    global STOP
    STOP = False

    threading.Thread(target=watch_for_escape, daemon=True).start()

    dx, dz = get_snapped_direction()

    m.echo(f"Auto miner online. Mining direction: ({dx}, {dz}). ESC to stop.")

    pos = m.player_position()
    x, y, z = map(int, map(math.floor, pos))

    segment = 0
    last_trash = time.time()

    try:
        while True:
            check_stop()

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
                    wait_until = time.time() + 0.45
                    while time.time() < wait_until:
                        check_stop()
                        time.sleep(0.05)
                finally:
                    m.player_press_forward(False)

                after = m.player_position()

                moved = math.sqrt((after[0]-before[0])**2 + (after[2]-before[2])**2)

                if moved < 0.2:
                    m.echo("[MOVE] stuck detected")

                    if not try_step_up(dx, dz, x, y, z):
                        raise Exception("Cannot move forward")

            x, z = fx, fz

            segment += 1

            auto_eat()

            now = time.time()
            if now - last_trash >= 60:
                drop_trash(dx, dz)
                last_trash = now

    except Exception as e:
        m.echo(f"[FATAL] {e}")
        if STOP_REASON not in ("user", "inventory_full"):
            discord_ping(f"Miner stopped: {e}")
        STOP = True

if __name__ == "__main__":
    main()