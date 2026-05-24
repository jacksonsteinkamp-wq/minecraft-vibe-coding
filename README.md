# Minescript Miner

## Scripts

| Script | What it does |
|---|---|
| `minerv3.py` | Basic auto-miner. Mines forward in a straight tunnel, drops trash every 60s. |
| `minerv4.py` | v3 + integrated auto-eat. Checks food every cycle, eats from offhand or hotbar. |
| `run_v4.py` | Same as v4, sourced from the `minerv4_pack/` module split. |
| `autoeat.py` | Standalone auto-eat. Run alongside anything. Checks food every 10s. |
| `dropstacktest.py` | Test script for trash dropping logic. |
| `clip_recorder.py` | Standalone screen recorder — see section below. |

## Hotbar Layout

| Slot | Item |
|---|---|
| 1-8 (internal 0-7) | Tools (pickaxes, shovels) |
| 9 (internal 8) | **Fortune pickaxe** — miner auto-selects it for ores |
| Offhand | **Food** — auto-eat checks offhand first, then hotbar |

Food can go in any hotbar slot too, but offhand is preferred since the miner never needs to select a different slot to eat from there.

## How to Run

```
/run minerv3
/run minerv4
w/run run_v4
/run autoeat
```

Press ESC to stop any script.

## Inventory Full

When the miner can't drop any more trash and ≥35/36 slots are full, it sends a Discord webhook and stops.

## Clip Recorder

`clip_recorder.py` is a standalone script (not run via Minescript) that continuously records your screen and saves the last 60 seconds whenever the miner stops or crashes.

**How it works:**
- Records the primary monitor at 5 FPS into a 60-second ring buffer
- Uses a Discord bot to watch the channel where the miner's stop/crash webhooks are posted
- On a matching message ("Miner stopped" / "Inventory full"), saves the buffer as an MP4 to `clips/`
- Press the hotkey (default F9) to save a manual clip anytime
- Beeps when a clip is saved
- On startup, also checks the last 20 messages in case the miner crashed while the recorder was off

**Setup:** Set `BOT_TOKEN`, `CHANNEL_ID`, and `HOTKEY` at the top of `clip_recorder.py`, then run:
```
python clip_recorder.py
```

**Dependencies** (pip install):
- `mss` — screen capture
- `opencv-python` — video encoding
- `discord.py` — Discord bot API
- `pynput` — global hotkey listener

**Notes:**
- `clips/` is in `.gitignore` — videos are large binaries that shouldn't be pushed to git
