import time
import minescript as m
from minescript_plus import Inventory

TRASH_ITEMS = {
    "minecraft:cobblestone",
    "minecraft:cobbled_deepslate",
    "minecraft:dirt",
    "minecraft:gravel",
    "minecraft:andesite",
    "minecraft:diorite",
    "minecraft:granite",
}

prev_total = 9999

while True:
    inv = m.player_inventory()

    hotbar_trash = [i.slot for i in inv if i.slot is not None and i.slot <= 8 and i.item in TRASH_ITEMS]
    if hotbar_trash:
        m.echo(f"[DROP] Hotbar trash: {hotbar_trash}")
        Inventory.drop_slots(hotbar_trash)

    inv = m.player_inventory()
    main_trash = [i.slot for i in inv if i.slot is not None and 9 <= i.slot <= 35 and i.item in TRASH_ITEMS]
    total_trash = len(hotbar_trash) + len(main_trash)

    if total_trash == 0:
        m.echo("[DROP] No trash found")
        break

    if total_trash >= prev_total:
        m.echo("[DROP] No progress — hotbar probably full")
        break
    prev_total = total_trash

    if not main_trash:
        break

    m.echo(f"[DROP] Shift-clicking {len(main_trash)} items: {main_trash}")
    Inventory.move_to_hotbar(main_trash, [])

    inv = m.player_inventory()
    new_hotbar_trash = [i.slot for i in inv if i.slot is not None and i.slot <= 8 and i.item in TRASH_ITEMS]
    if new_hotbar_trash:
        m.echo(f"[DROP] Dropping moved trash: {new_hotbar_trash}")
        Inventory.drop_slots(new_hotbar_trash)
