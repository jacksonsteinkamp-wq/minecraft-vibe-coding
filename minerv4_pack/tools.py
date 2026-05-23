import json
import time
import minescript as m
from .config import PICK_TIER, SHOVEL_ITEMS, SHOVEL_BLOCKS, ORE_BLOCKS

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

def _pick_damage(pick):
    try:
        nbt = json.loads(pick.nbt) if pick.nbt else {}
        return nbt.get("components", {}).get("minecraft:damage", 0)
    except Exception:
        return 0

def best_pick(picks):
    return max(picks, key=lambda x: PICK_TIER.get(x[1].item, -1))

def worst_pick(picks):
    return min(picks, key=lambda x: (PICK_TIER.get(x[1].item, -1), _pick_damage(x[1])))

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
    if shovels:
        slot, item = shovels[0]
        m.player_inventory_select_slot(slot)
        time.sleep(0.1)
        return
    inv = m.player_inventory()
    occupied = set()
    for i in inv:
        if i.slot is not None and i.slot <= 8:
            occupied.add(i.slot)
            if i.item not in PICK_TIER and i.item not in SHOVEL_ITEMS:
                m.player_inventory_select_slot(i.slot)
                time.sleep(0.1)
                return
    for slot in range(9):
        if slot not in occupied:
            m.player_inventory_select_slot(slot)
            time.sleep(0.1)
            return
    raise Exception("No shovel or usable hotbar slot")

def select_tool(block):
    if block in SHOVEL_BLOCKS:
        select_shovel()
    else:
        select_pick(block)
