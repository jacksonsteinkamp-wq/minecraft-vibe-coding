# Minescript Miner

## Features

| Feature | Detail |
|---|---|
| **Auto‑mine** | Mines blocks ahead in a straight tunnel (head + feet level) |
| **Best‑tool selection** | Picks the correct tool for each block — shovel for dirt/gravel, pickaxe for stone/ore. Selects lowest‑tier usable tool first to save higher tiers for ores. Uses NBT damage to pick the most‑durable item within the same tier. Falls back to fist if no tool. |
| **Fortune pickaxe** | Auto‑selects fortune pickaxe (slot 9) for ore blocks |
| **Auto‑eat** | Checks hunger every loop cycle; eats from offhand or any hotbar slot; ESC‑safe (chunked sleeps) |
| **Trash dropping** | Drops cobblestone, dirt, gravel, andesite, diorite, granite from hotbar every 60s. Uses number‑key select + `drop(True)` with 0.3s delay per slot. |
| **Inventory management** | Every 10s, shift‑clicks non‑tool/non‑food items from hotbar into main inventory to keep the hotbar clean for mining |
| **Gravel handling** | Detects gravel/sand ahead; holds W forward while mining all blocks in the column; clears up to 15 gravity blocks above the player; descends back to original Y when done |
| **Wall‑ahead detection** | If the player doesn't move after pressing forward, mines any solid blocks at head, feet, and step level |
| **Step‑up** | If forward mining fails, mines 6 blocks (player head, above head, front step, front feet, front head, above front) to step up, retries 3 times, digs below as last resort |
| **Stuck handling** | Tracks a stuck timer; resets on any successful movement; after 120s of being stuck, raises an exception → Discord ping |
| **Discord ping** | Sends a webhook on actual crashes / inventory full / stuck timeout (not on user ESC stop) |
| **ESC shutdown** | ESC immediately stops all loops via a daemon thread watcher; `check_stop()` every 0.05s in all blocking loops |
| **Ore‑vein mode** *(disabled)* | BFS flood‑fill mines connected ore veins through walls. Check `minerv4_pack/vein.py`. Set `# x, z = mine_ores(...)` in `main.py` to re‑enable. |

## Usage

```
/w run run_v4
```

The miner starts mining in the direction you're facing. ESC to stop.

## Hotbar Layout

| Slot | Item |
|---|---|
| 1–8 | Tools (pickaxes, shovels, swords, etc.) |
| 9 | **Fortune pickaxe** — auto‑selected for ores |
| Offhand | **Food** — auto‑eat checks offhand first, then hotbar |

Food can go in any hotbar slot. Tools in slots 1–8, highest durability pickaxe per tier is auto‑selected.

## Inventory & Trash

- **Every 10s**: non‑tool, non‑food items in the hotbar are shift‑clicked into the main inventory
- **Every 60s**: trash blocks (cobblestone, dirt, gravel, andesite, diorite, granite) are dropped from the hotbar
- If ≥35/36 inventory slots are full and no trash can be dropped, the miner sends a Discord alert and stops

## Clip Recorder

`clip_recorder.py` is a standalone script (not run via Minescript) that records the screen into a 60‑second ring buffer. It saves a clip when the Discord bot detects a miner stop/crash message, or on F9 hotkey.

**Run:**
```
python clip_recorder.py
```

Dependencies: `mss`, `opencv-python`, `discord.py`, `pynput`. See `clip_recorder.py` for token/channel/hotkey config.
