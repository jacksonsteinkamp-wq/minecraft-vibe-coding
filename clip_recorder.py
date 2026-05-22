"""
clip_recorder.py — Minecraft Miner Clip Recorder
Saves a 60-second screen capture whenever the miner stops or crashes.
"""

import os
import sys
import json
import time
import threading
from collections import deque

SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "clip_recorder_config.json")
CLIPS_DIR   = os.path.join(SCRIPT_DIR, "clips")

FPS              = 5
BUFFER_SECONDS   = 60
TRIGGER_KEYWORDS = ["Miner stopped", "Inventory full"]
DEFAULT_HOTKEY   = "f9"
STARTUP_GRACE    = 20

_buffer      = deque()
_buffer_lock = threading.Lock()
_capturing   = True
_start_time  = time.time()


def _beep():
    try:
        import winsound
        winsound.Beep(880, 200)
    except Exception:
        pass


def _load_or_create_config() -> dict:
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH) as f:
                cfg = json.load(f)
            if cfg.get("bot_token") and cfg.get("channel_id"):
                if "hotkey" not in cfg:
                    cfg["hotkey"] = DEFAULT_HOTKEY
                    with open(CONFIG_PATH, "w") as f:
                        json.dump(cfg, f, indent=2)
                return cfg
        except Exception:
            pass

    print()
    print("  ┌─────────────────────────────────────────────┐")
    print("  │   Clip Recorder — First-Time Setup          │")
    print("  │   (saved to clip_recorder_config.json)      │")
    print("  └─────────────────────────────────────────────┘")
    print()

    token = input("  Discord bot token: ").strip()
    while not token:
        token = input("  Discord bot token: ").strip()

    channel_raw = input("  Discord channel ID: ").strip()
    while not channel_raw.isdigit():
        channel_raw = input("  Discord channel ID: ").strip()

    print("  Hotkey to save a clip anytime (e.g. f9, f12):")
    hotkey = input(f"  [{DEFAULT_HOTKEY}]: ").strip() or DEFAULT_HOTKEY

    cfg = {"bot_token": token, "channel_id": int(channel_raw), "hotkey": hotkey}
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)
    print(f"  Saved to {CONFIG_PATH}\n")
    return cfg


def _capture_loop():
    try:
        import mss
        import numpy as np
    except ImportError as e:
        print(f"[REC] Missing package: {e}")
        return

    buffer_ready = False
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        while _capturing:
            t0 = time.time()
            try:
                frame = np.array(sct.grab(monitor))
            except Exception:
                time.sleep(0.5)
                continue
            with _buffer_lock:
                _buffer.append((t0, frame))
                cutoff = t0 - BUFFER_SECONDS
                while _buffer and _buffer[0][0] < cutoff:
                    _buffer.popleft()
            if not buffer_ready and len(_buffer) >= BUFFER_SECONDS * FPS * 0.95:
                print(f"[REC] Buffer full ({BUFFER_SECONDS}s)")
                buffer_ready = True
            sleep_for = (1.0 / FPS) - (time.time() - t0)
            if sleep_for > 0:
                time.sleep(sleep_for)


def _save_clip(reason=""):
    with _buffer_lock:
        snapshot = list(_buffer)
    if not snapshot:
        print("[REC] Buffer empty")
        return
    try:
        import cv2
    except ImportError:
        print("[REC] Install opencv-python")
        return
    os.makedirs(CLIPS_DIR, exist_ok=True)
    h, w = snapshot[0][1].shape[:2]
    ts = time.strftime("%Y%m%d_%H%M%S")
    path = os.path.join(CLIPS_DIR, f"clip_{ts}.mp4")
    out = None
    for codec in ("mp4v", "avc1"):
        out = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*codec), FPS, (w, h))
        if out.isOpened():
            break
        out = None
    if out is None:
        return
    for _, frame in snapshot:
        out.write(cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR))
    out.release()
    kb = os.path.getsize(path) // 1024
    print(f"[REC] Saved: {path} ({kb} KB)")
    _beep()


def _start_hotkey_listener(hotkey_str):
    try:
        from pynput import keyboard as kb
    except ImportError:
        print("[REC] Install pynput for hotkey")
        return

    parts = ["<" + p + ">" if len(p) > 1 and not p.startswith("<") else p for p in hotkey_str.split("+")]
    normalised = "+".join(parts)

    def on_activate():
        threading.Thread(target=_save_clip, args=("hotkey",), daemon=True).start()

    try:
        listener = kb.GlobalHotKeys({normalised: on_activate})
        listener.start()
        print(f"[REC] Hotkey: {hotkey_str}")
    except Exception as e:
        print(f"[REC] Hotkey failed: {e}")


async def _discord_listener(cfg):
    try:
        import discord
    except ImportError:
        print("[REC] Install discord.py")
        return

    intents = discord.Intents.default()
    intents.message_content = True

    class Bot(discord.Client):
        async def on_ready(self):
            print(f"[REC] Discord logged in as {self.user}")
            ch = self.get_channel(cfg["channel_id"])
            if not ch:
                try:
                    ch = await self.fetch_channel(cfg["channel_id"])
                except Exception as e:
                    print(f"[REC] Cannot access channel: {e}")
                    return
            if time.time() - _start_time > STARTUP_GRACE:
                try:
                    async for msg in ch.history(limit=20):
                        for kw in TRIGGER_KEYWORDS:
                            if kw in msg.content:
                                age = time.time() - msg.created_at.timestamp()
                                if age < 300:
                                    print(f"[REC] Found in history: {msg.content[:80]}")
                                    _save_clip("missed while offline")
                                return
                except Exception:
                    pass
            print("[REC] Listening...")

        async def on_message(self, msg):
            if msg.channel.id != cfg["channel_id"]:
                return
            for kw in TRIGGER_KEYWORDS:
                if kw in msg.content:
                    print(f"[REC] Trigger: {msg.content[:80]}")
                    _save_clip(msg.content[:60])
                    return

    try:
        await Bot(intents=intents).start(cfg["bot_token"])
    except discord.LoginFailure:
        print("[REC] Invalid token — delete clip_recorder_config.json and retry")


if __name__ == "__main__":
    print("  Minecraft Miner Clip Recorder")
    print(f"  Buffer: {BUFFER_SECONDS}s @ {FPS}FPS")
    print()
    cfg = _load_or_create_config()
    cap_thread = threading.Thread(target=_capture_loop, daemon=True)
    cap_thread.start()
    time.sleep(1)
    if not cap_thread.is_alive():
        print("[REC] Capture thread failed to start")
        sys.exit(1)
    _start_hotkey_listener(cfg["hotkey"])
    import asyncio
    try:
        asyncio.run(_discord_listener(cfg))
    except KeyboardInterrupt:
        print("\n[REC] Stopped")
        _capturing = False
