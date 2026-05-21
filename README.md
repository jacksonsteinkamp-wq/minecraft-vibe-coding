# Minescript Miner

## Scripts

| Script | What it does |
|---|---|
| `minerv3.py` | Basic auto-miner. Mines forward in a straight tunnel, drops trash every 60s. |
| `minerv4.py` | v3 + integrated auto-eat. Checks food every cycle, eats from offhand or hotbar. |
| `autoeat.py` | Standalone auto-eat. Run alongside anything. Checks food every 10s. |
| `dropstacktest.py` | Test script for trash dropping logic. |

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
/run autoeat
```

Press ESC to stop any script.

## Inventory Full

When the miner can't drop any more trash and ≥35/36 slots are full, it sends a Discord webhook and stops.


we will add the pinging and patterns and other settings with ui later. one field can be discord id so the bot can ping them "Hello <@1130279768856723596>" pings "Hello @MarsReaper22"