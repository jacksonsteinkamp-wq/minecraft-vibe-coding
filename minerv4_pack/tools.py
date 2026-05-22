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
