# minerv2: v1 + direction detection from player yaw + ESC stop + camera alignment + try_step_up recovery.
import time
import math
import threading
import subprocess
import minescript as m
import winsound

global python_path
python_path = r"C:\Python314\python.exe"

# ─── ESC kill switch ──────────────────────────────────────────────────────────

STOP = False
ESCAPE_KEY = 256  # GLFW key code for Escape

def watch_for_escape():
    global STOP
    with m.EventQueue() as eq:
        eq.register_key_listener()
        while not STOP:
            try:
                event = eq.get(timeout=0.2)
                if event.key == ESCAPE_KEY and event.action == 1:  # 1 = key down
                    STOP = True
                    m.echo("[ESC] Kill switch triggered.")
                    
                    return
            except Exception:
                pass  # timeout / queue.Empty, keep looping

def check_stop():
    if STOP:
        raise Exception("Stopped by user (ESC)")

# ─── Block categories ─────────────────────────────────────────────────────────

SHOVEL_BLOCKS = {
    "minecraft:dirt", "minecraft:gravel", "minecraft:sand",
    "minecraft:grass_block", "minecraft:coarse_dirt", "minecraft:rooted_dirt",
    "minecraft:muddy_mangrove_roots", "minecraft:mud", "minecraft:clay",
    "minecraft:soul_sand", "minecraft:soul_soil", "minecraft:snow",
    "minecraft:snow_block", "minecraft:powder_snow",
}

ORE_BLOCKS = {
    "minecraft:coal_ore", "minecraft:deepslate_coal_ore",
    "minecraft:iron_ore", "minecraft:deepslate_iron_ore",
    "minecraft:copper_ore", "minecraft:deepslate_copper_ore",
    "minecraft:gold_ore", "minecraft:deepslate_gold_ore",
    "minecraft:redstone_ore", "minecraft:deepslate_redstone_ore",
    "minecraft:emerald_ore", "minecraft:deepslate_emerald_ore",
    "minecraft:lapis_ore", "minecraft:deepslate_lapis_ore",
    "minecraft:diamond_ore", "minecraft:deepslate_diamond_ore",
    "minecraft:nether_gold_ore", "minecraft:nether_quartz_ore",
    "minecraft:ancient_debris",
}

# Tier order: higher index = better
PICK_TIER = {
    "minecraft:wooden_pickaxe":    0,
    "minecraft:stone_pickaxe":     1,
    "minecraft:golden_pickaxe":    2,
    "minecraft:iron_pickaxe":      3,
    "minecraft:diamond_pickaxe":   4,
    "minecraft:netherite_pickaxe": 5,
}

SHOVEL_ITEMS = {
    "minecraft:wooden_shovel", "minecraft:stone_shovel",
    "minecraft:iron_shovel", "minecraft:golden_shovel",
    "minecraft:diamond_shovel", "minecraft:netherite_shovel",
}

# ─── Tool helpers ─────────────────────────────────────────────────────────────

def is_fortune_pick(item_stack):
    result = bool(item_stack.nbt and "Fortune" in item_stack.nbt)
    return result

def get_hotbar_tools():
    """Returns (picks, shovels) where each is a list of (slot, item_stack) from hotbar only."""
    inventory = m.player_inventory()
    m.echo(f"[DEBUG] Raw inventory: {[(i.item, i.slot, i.nbt) for i in inventory if i.slot is not None and i.slot <= 8]}")
    picks = []
    shovels = []
    for item in inventory:
        if item.slot is None or item.slot > 8:
            continue
        if item.item in PICK_TIER:
            picks.append((item.slot, item))
        elif item.item in SHOVEL_ITEMS:
            shovels.append((item.slot, item))
    m.echo(f"[DEBUG] Detected picks: {[(s, i.item, 'FORTUNE' if is_fortune_pick(i) else 'normal') for s,i in picks]}")
    m.echo(f"[DEBUG] Detected shovels: {[(s, i.item) for s,i in shovels]}")
    return picks, shovels

def best_pick(pick_list):
    """Returns the (slot, item_stack) with the highest tier from a list."""
    return max(pick_list, key=lambda si: PICK_TIER.get(si[1].item, -1))

def select_pickaxe(block_type):
    picks, _ = get_hotbar_tools()
    if not picks:
        raise Exception("No pickaxes left in hotbar! Stopping.")

    is_ore = block_type in ORE_BLOCKS
    fortune_picks  = [(s, i) for s, i in picks if is_fortune_pick(i)]
    regular_picks  = [(s, i) for s, i in picks if not is_fortune_pick(i)]

    m.echo(f"[DEBUG] Selecting pick for block '{block_type}' | is_ore={is_ore} | fortune_available={len(fortune_picks)>0} | regular_available={len(regular_picks)>0}")

    if is_ore and fortune_picks:
        # Ore + Fortune available: use best Fortune pick
        slot, item = best_pick(fortune_picks)
        m.echo(f"[TOOL] Ore! Using Fortune pick '{item.item}' in slot {slot}")
    elif regular_picks:
        # Use best regular pick (non-ore always comes here; ore falls back here if no Fortune)
        slot, item = best_pick(regular_picks)
        if is_ore:
            m.echo(f"[TOOL] Ore but no Fortune pick -- using best regular pick '{item.item}' in slot {slot}")
        else:
            m.echo(f"[TOOL] Using best regular pick '{item.item}' in slot {slot}")
    elif is_ore and fortune_picks:
        # Only Fortune picks left but this is an ore -- still fine
        slot, item = best_pick(fortune_picks)
        m.echo(f"[TOOL] Only Fortune picks left, but block is ore -- using '{item.item}' in slot {slot}")
    else:
        raise Exception(f"No usable pickaxe for block '{block_type}'! Stopping.")

    m.echo(f"[DEBUG] Calling player_inventory_select_slot({slot})")
    m.player_inventory_select_slot(slot)
    time.sleep(0.1)

def select_shovel():
    _, shovels = get_hotbar_tools()
    if not shovels:
        raise Exception("No shovels left in hotbar! Stopping.")
    slot, item = shovels[0]
    m.echo(f"[TOOL] Soft block -- switching to shovel '{item.item}' in slot {slot}")
    m.player_inventory_select_slot(slot)
    time.sleep(0.1)

def select_tool_for_block(block_type):
    if block_type in SHOVEL_BLOCKS:
        select_shovel()
    else:
        select_pickaxe(block_type)

# ─── Discord ──────────────────────────────────────────────────────────────────

def call_discord_webhook(message_text):
    m.echo(f"[DISCORD] Sending: {message_text}")
    result = subprocess.Popen(
        [python_path, r"C:\Users\jackn\AppData\Roaming\.minecraft\minescript\discord_webhook2.py", message_text],
    )
    m.echo(f"[DISCORD] Popen returncode: {result.returncode}")

# ─── Camera / direction ───────────────────────────────────────────────────────

def get_snapped_direction():
    yaw, pitch = m.player_orientation()
    norm_yaw = yaw % 360
    if norm_yaw < 0:
        norm_yaw += 360
    m.echo(f"[DEBUG] Raw yaw={yaw:.1f} norm_yaw={norm_yaw:.1f}")

    if 315 <= norm_yaw or norm_yaw < 45:
        return 0, 1, "SOUTH (+Z)"
    elif 45 <= norm_yaw < 135:
        return -1, 0, "WEST (-X)"
    elif 135 <= norm_yaw < 225:
        return 0, -1, "NORTH (-Z)"
    else:
        return 1, 0, "EAST (+X)"

def align_player_camera(dx, dz):
    pos = m.player_position()
    px, py, pz = pos[0], pos[1], pos[2]
    target_x = px + (dx * 5)
    target_y = py + 1.62
    target_z = pz + (dz * 5)
    m.echo(f"[DEBUG] Camera realign -> target ({target_x:.1f}, {target_y:.1f}, {target_z:.1f})")
    m.player_look_at(target_x, target_y, target_z)
    time.sleep(0.15)

# ─── Mining ───────────────────────────────────────────────────────────────────

def mine_block_at(x, y, z):
    block_type = m.getblocklist([(x, y, z)])[0]
    m.echo(f"[DEBUG] mine_block_at ({x},{y},{z}) -> '{block_type}'")

    if block_type == "minecraft:air":
        m.echo(f"[DEBUG] Block is air, skipping.")
        return

    select_tool_for_block(block_type)

    m.player_look_at(x + 0.5, y + 0.5, z + 0.5)
    time.sleep(0.05)

    timeout = time.time() + 10
    ticks = 0
    while m.getblocklist([(x, y, z)])[0] != "minecraft:air":
        check_stop()
        if time.time() > timeout:
            raise Exception(f"Block at ({x},{y},{z}) took too long to break! Tool broken?")
        m.player_press_attack(True)
        time.sleep(0.05)
        ticks += 1
    m.player_press_attack(False)
    m.echo(f"[DEBUG] Broke '{block_type}' in {ticks} ticks.")

# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    global STOP
    STOP = False

    m.echo("=== Auto-Miner v2 starting (debug mode). Press ESC to stop. ===")
    stop_reason = "Mining done"

    esc_thread = threading.Thread(target=watch_for_escape, daemon=True)
    esc_thread.start()
    m.echo("[DEBUG] ESC watcher thread started.")

    try:
        dx, dz, dir_name = get_snapped_direction()
        m.echo(f"Direction locked: {dir_name} (dx={dx}, dz={dz})")
        align_player_camera(dx, dz)

        pos = m.player_position()
        current_x = int(math.floor(pos[0]))
        current_y = int(math.floor(pos[1]))
        current_z = int(math.floor(pos[2]))
        m.echo(f"[DEBUG] Start position: ({current_x}, {current_y}, {current_z})")

        picks, shovels = get_hotbar_tools()
        fortune = [s for s, i in picks if is_fortune_pick(i)]
        regular = [s for s, i in picks if not is_fortune_pick(i)]
        m.echo(f"[INIT] Regular picks: slots {regular} | Fortune picks: slots {fortune} | Shovels: slots {[s for s,i in shovels]}")

        for step in range(20):
            check_stop()

            if step > 0 and step % 3 == 0:
                m.echo(f"[DEBUG] Step {step+1}: periodic camera realign")
                align_player_camera(dx, dz)

            tx = current_x + dx
            tz = current_z + dz
            m.echo(f"--- Step {step+1}/20 | target column: ({tx}, *, {tz}) ---")

            mine_block_at(tx, current_y + 1, tz)
            mine_block_at(tx, current_y, tz)
            
            

                m.echo(f"[DEBUG] Moving forward...")
                m.player_press_forward(True)
                time.sleep(0.45)
                m.player_press_forward(False)
                time.sleep(0.05)

                current_x = tx
                current_z = tz
                m.echo(f"[DEBUG] New position: ({current_x}, {current_y}, {current_z})")

        m.echo("=== Mining complete! ===")

    except Exception as e:
        msg = str(e)
        if "Stopped by user" in msg:
            stop_reason = None
            m.echo("[ESC] Bot stopped cleanly. No Discord notification.")
        else:
            stop_reason = f"Bot stopped: {msg}"
            m.echo(f"[ERROR] {msg}")

    finally:
        STOP = True
        m.player_press_attack(False)
        m.echo("[DEBUG] Attack key released.")
        if stop_reason:
            call_discord_webhook(stop_reason)

if __name__ == "__main__":
    main()