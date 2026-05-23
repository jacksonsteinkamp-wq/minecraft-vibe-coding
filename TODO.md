## Done
- Screen clip recorder: standalone `clip_recorder.py` — records 60s ring buffer, saves MP4 when the miner's Discord webhook message is detected in a channel

## Planned
- Better ore grabbing (e.g. vein mine, silk touch vs fortune logic)
- Craft raw ores/cobble into blocks for space efficiency
- Auto-use XP bottles for mending tools
- Stop and alert before a tool breaks (durability threshold)
- UI / config system (Replit or similar):
  - Mining pattern (straight, staircase, wide tunnel, etc.)
  - Tunnel distance from base
  - Discord ID for DM pings (@user)
  - Discord webhook URL
  - Tool break threshold (for both fortune and otherwise)
  - All tunable constants (trash interval, food threshold, etc.)
  - Slot for Fortune pick (if there is one)
- Auto-start clip recorder or integrate into UI
