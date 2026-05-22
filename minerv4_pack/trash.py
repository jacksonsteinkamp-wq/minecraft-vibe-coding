import time
import minescript as m
from minescript_plus import Inventory, mc
from . import state
from .discord import discord_ping
from .config import TRASH_ITEMS

def _drop_slot(slot):
    m.player_inventory_select_slot(slot)
    time.sleep(0.1)
    mc.player.drop(True)
    time.sleep(0.3)
    state.check_stop()

def _drop_hotbar_trash(slots):
    for slot in slots:
        _drop_slot(slot)

def drop_trash(dx, dz):
    m.echo("[TRASH] dumping junk")
    pos = m.player_position()
    m.player_look_at(pos[0] - dx * 5, pos[1] + 1.6, pos[2] - dz * 5)
    time.sleep(0.2)
    prev_total = 9999
    while True:
        state.check_stop()
        inv = m.player_inventory()
        hotbar_trash = [i.slot for i in inv if i.slot is not None and i.slot <= 8 and i.item in TRASH_ITEMS]
        if hotbar_trash:
            _drop_hotbar_trash(hotbar_trash)
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
        state.check_stop()
        inv = m.player_inventory()
        new_hotbar_trash = [i.slot for i in inv if i.slot is not None and i.slot <= 8 and i.item in TRASH_ITEMS]
        if new_hotbar_trash:
            _drop_hotbar_trash(new_hotbar_trash)
    state.check_stop()
    pos = m.player_position()
    m.player_look_at(pos[0] + dx * 5, pos[1] + 1.6, pos[2] + dz * 5)
    time.sleep(0.2)
    inv = m.player_inventory()
    occupied = len([i for i in inv if i.slot is not None and i.slot <= 35])
    if occupied >= 35:
        m.echo("[TRASH] Inventory full, stopping")
        discord_ping("Inventory full! Miner stopped.")
        state.STOP = True
        state.STOP_REASON = "inventory_full"
