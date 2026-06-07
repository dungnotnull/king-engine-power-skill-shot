#!/usr/bin/env python3
"""
king_engine.py — Main Orchestrator for King Engine Power Skill Shot
👑 "The strongest agent in the coding arena" 👑

Usage:
    python king_engine.py --trigger battle_start   # Fire King Engine
    python king_engine.py --trigger victory        # Fire Victory sequence
    python king_engine.py --test battle_start      # Test without cooldown
    python king_engine.py --test victory
    python king_engine.py --monitor                # Read stdin, auto-detect phases
    python king_engine.py --setup                  # Download audio + verify install
"""

import sys
import os
import time
import argparse
import threading
import json
from pathlib import Path

# Paths
SKILL_DIR = Path(__file__).parent.parent
SCRIPTS_DIR = Path(__file__).parent
ASSETS_DIR = SCRIPTS_DIR / "assets"
STATE_FILE = Path("/tmp/king_engine_state.json")

# ─── State Management ───────────────────────────────────────────────────────────

def load_state() -> dict:
    """Load persistent state (cooldowns, current phase)."""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "phase": "IDLE",
        "last_battle_start": 0,
        "last_victory": 0,
        "planning_score": 0,
    }


def save_state(state: dict):
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f)
    except Exception:
        pass


def reset_state():
    save_state({
        "phase": "IDLE",
        "last_battle_start": 0,
        "last_victory": 0,
        "planning_score": 0,
    })


# ─── Cooldown Checks ────────────────────────────────────────────────────────────

BATTLE_START_COOLDOWN = 60    # seconds
VICTORY_COOLDOWN = 300        # 5 minutes


def can_fire_battle_start(state: dict, bypass_cooldown: bool = False) -> bool:
    if bypass_cooldown:
        return True
    elapsed = time.time() - state.get("last_battle_start", 0)
    return elapsed > BATTLE_START_COOLDOWN


def can_fire_victory(state: dict, bypass_cooldown: bool = False) -> bool:
    if bypass_cooldown:
        return True
    elapsed = time.time() - state.get("last_victory", 0)
    return elapsed > VICTORY_COOLDOWN


# ─── Fire Sequences ─────────────────────────────────────────────────────────────

def fire_battle_start(bypass_cooldown: bool = False):
    """Fire the King Engine sequence."""
    state = load_state()

    if not can_fire_battle_start(state, bypass_cooldown):
        remaining = int(BATTLE_START_COOLDOWN - (time.time() - state["last_battle_start"]))
        print(f"[King Engine] Cooldown active — {remaining}s remaining", file=sys.stderr)
        return

    # Update state
    state["phase"] = "IMPLEMENTING"
    state["last_battle_start"] = time.time()
    save_state(state)

    # Fire audio in background thread
    audio_thread = threading.Thread(
        target=_play_audio, args=("king",), daemon=True
    )
    audio_thread.start()

    # Fire terminal FX (foreground — the visual is the show)
    _run_terminal_fx("king")


def fire_victory(bypass_cooldown: bool = False):
    """Fire the Victory sequence."""
    state = load_state()

    if not can_fire_victory(state, bypass_cooldown):
        remaining = int(VICTORY_COOLDOWN - (time.time() - state["last_victory"]))
        print(f"[King Engine] Victory cooldown active — {remaining}s remaining", file=sys.stderr)
        return

    # Update state
    state["phase"] = "COMPLETED"
    state["last_victory"] = time.time()
    save_state(state)

    # Fire audio in background thread
    audio_thread = threading.Thread(
        target=_play_audio, args=("victory",), daemon=True
    )
    audio_thread.start()

    # Fire terminal FX
    _run_terminal_fx("victory")

    # Reset phase for next task
    time.sleep(0.5)
    state["phase"] = "IDLE"
    state["planning_score"] = 0
    save_state(state)


# ─── Internal Runners ───────────────────────────────────────────────────────────

def _play_audio(mode: str):
    """Try to play audio — silently falls back on failure."""
    try:
        from audio_player import AudioPlayer
        player = AudioPlayer(assets_dir=ASSETS_DIR)
        player.play(mode)
    except ImportError:
        # audio_player not importable — try direct
        try:
            import subprocess
            audio_file = ASSETS_DIR / (
                "king_engine.mp3" if mode == "king" else "one_punch_ost.mp3"
            )
            if audio_file.exists():
                _play_file(str(audio_file))
            else:
                _play_beep_fallback(mode)
        except Exception:
            pass  # Silent fail — audio is bonus
    except Exception:
        pass


def _play_file(path: str):
    """Play audio file using system command."""
    import subprocess
    platform = sys.platform

    if platform == "darwin":
        subprocess.Popen(["afplay", path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    elif platform.startswith("linux"):
        # Try paplay first, then aplay
        for cmd in [["paplay", path], ["aplay", path], ["mpg123", "-q", path]]:
            try:
                subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return
            except FileNotFoundError:
                continue
    elif platform == "win32":
        import winsound
        # winsound only supports WAV — try pygame instead
        try:
            import pygame
            pygame.mixer.init()
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()
        except Exception:
            pass


def _play_beep_fallback(mode: str):
    """Generate audio pattern using system beep when no audio files available."""
    import subprocess
    platform = sys.platform

    if mode == "king":
        # King Engine: low, intimidating, building
        pattern = [
            (150, 600),   # DOKI
            (0, 400),     # silence
            (150, 600),   # DOKI
            (0, 300),     # silence
            (150, 200),   # DOKI DOKI DOKI DOKI
            (150, 200),
            (150, 200),
            (150, 200),
            (200, 400),   # higher tension
            (250, 800),   # peak
        ]
    else:
        # Victory: triumphant ascending melody
        pattern = [
            (440, 200),   # A4
            (494, 200),   # B4
            (523, 200),   # C5
            (587, 400),   # D5
            (659, 400),   # E5
            (784, 800),   # G5 — triumph!
        ]

    if platform == "win32":
        import winsound
        for freq, dur in pattern:
            if freq > 0:
                winsound.Beep(freq, dur)
            else:
                time.sleep(dur / 1000)
    else:
        # Terminal bell as approximate
        for freq, dur in pattern[:3]:
            sys.stdout.write("\a")
            sys.stdout.flush()
            time.sleep(dur / 1000)


def _run_terminal_fx(mode: str):
    """Run terminal animation — tries script first, falls back to inline."""
    try:
        from terminal_fx import TerminalFX
        fx = TerminalFX()
        if mode == "king":
            fx.play_king_engine()
        else:
            fx.play_victory()
    except ImportError:
        # Inline fallback
        _render_inline_fx(mode)
    except Exception as e:
        _render_inline_fx(mode)


def _render_inline_fx(mode: str):
    """Minimal inline fallback terminal FX."""
    ansi = sys.stdout.isatty() and os.environ.get("TERM") != "dumb"
    R = "\033[0m"
    B = "\033[1m"
    Y = "\033[33m"
    RD = "\033[31m"
    GR = "\033[92m"
    CY = "\033[36m"

    if mode == "king":
        frames = [
            (f"\n{B}{Y}╔══════════════════════════════════════════╗{R}\n"
             f"{B}{Y}║   👑  KING ENGINE ACTIVATED  👑          ║{R}\n"
             f"{B}{Y}╚══════════════════════════════════════════╝{R}\n", 0.6),
            (f"\n{B}{RD}  💀  D  O  K  I  .  .  .{R}\n", 0.5),
            (f"\n{B}{RD}  💀  D  O  K  I  .  .  .{R}\n", 0.4),
            (f"\n{B}{RD}  💀  D O K I  D O K I  D O K I  D O K I{R}\n", 0.3),
            (f"\n{B}{RD}████████████████████████████████████████████{R}\n"
             f"{B}{RD}█  D O K I  D O K I  D O K I  D O K I  D  █{R}\n"
             f"{B}{RD}████████████████████████████████████████████{R}\n", 0.8),
            (f"\n{B}{Y}⚡  AGENT ENTERING COMBAT MODE  ⚡{R}\n"
             f"{B}{Y}[ KING ENGINE : MAXIMUM OUTPUT ]{R}\n\n", 1.5),
        ]
    else:  # victory
        frames = [
            (f"\n{B}{Y}★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★{R}\n", 0.15),
            (f"\n{B}{CY}╔══════════════════════════════════════════╗{R}\n"
             f"{B}{CY}║      ⚡  ONE PUUUUNCH!!!  ⚡              ║{R}\n"
             f"{B}{CY}╚══════════════════════════════════════════╝{R}\n", 0.8),
            (f"\n{B}{GR}💥 💥 💥 TASK ANNIHILATED 💥 💥 💥{R}\n", 0.4),
            (f"\n{B}{GR}✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅{R}\n"
             f"{B}{Y}  ★ VICTORY ★ VICTORY ★ VICTORY ★{R}\n"
             f"{B}{GR}✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅{R}\n", 1.0),
            (f"\n{B}{GR}┌────────────────────────────────────────┐{R}\n"
             f"{B}{GR}│  ✅  MISSION COMPLETE                  │{R}\n"
             f"{B}{GR}│  👊  ONE PUNCH WAS ALL IT TOOK         │{R}\n"
             f"{B}{GR}└────────────────────────────────────────┘{R}\n\n", 2.0),
        ]

    if not ansi:
        # Strip ANSI for dumb terminals
        import re
        frames = [(re.sub(r'\033\[[^m]*m', '', f[0]), f[1]) for f in frames]

    for content, delay in frames:
        print(content, end="", flush=True)
        time.sleep(delay)


# ─── Monitor Mode ───────────────────────────────────────────────────────────────

def monitor_mode():
    """
    Read stdin line by line and auto-detect phases.
    Use: python king_engine.py --monitor
    Then pipe or paste agent output into it.
    """
    try:
        from phase_detector import PhaseDetector
        detector = PhaseDetector()
    except ImportError:
        print("[King Engine] phase_detector.py not found — monitor mode unavailable", file=sys.stderr)
        sys.exit(1)

    print("[King Engine] 👑 Monitor mode active — watching for phase transitions...", file=sys.stderr)

    for line in sys.stdin:
        event = detector.process_line(line)
        if event == "BATTLE_START":
            print(f"\n[King Engine] 🔥 BATTLE START DETECTED\n", file=sys.stderr)
            fire_battle_start()
        elif event == "VICTORY":
            print(f"\n[King Engine] 🏆 VICTORY DETECTED\n", file=sys.stderr)
            fire_victory()


# ─── Setup Mode ────────────────────────────────────────────────────────────────

def setup_mode():
    """Download audio files and verify installation."""
    print("👑 King Engine Power Skill Shot — Setup\n")

    # Check pygame
    try:
        import pygame
        print("✅ pygame: installed")
    except ImportError:
        print("⚠️  pygame: not found — run: pip install pygame --break-system-packages")

    # Check audio files
    king_audio = ASSETS_DIR / "king_engine.mp3"
    victory_audio = ASSETS_DIR / "one_punch_ost.mp3"

    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    if king_audio.exists():
        print(f"✅ King Engine audio: {king_audio}")
    else:
        print(f"⚠️  King Engine audio: NOT FOUND at {king_audio}")
        print("   → Place king_engine.mp3 in the assets/ folder")
        print("   → Or run: python audio_player.py --download-all")

    if victory_audio.exists():
        print(f"✅ Victory audio: {victory_audio}")
    else:
        print(f"⚠️  Victory audio: NOT FOUND at {victory_audio}")
        print("   → Place one_punch_ost.mp3 in the assets/ folder")
        print("   → Or run: python audio_player.py --download-all")

    print("\n🧪 Running terminal FX test in 2 seconds...")
    time.sleep(2)
    print("\n--- KING ENGINE TEST ---")
    fire_battle_start(bypass_cooldown=True)
    time.sleep(1)
    print("\n--- VICTORY TEST ---")
    fire_victory(bypass_cooldown=True)
    print("\n✅ Setup complete!")


# ─── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="👑 King Engine Power Skill Shot — Battle system for AI coding agents"
    )
    parser.add_argument(
        "--trigger", choices=["battle_start", "victory"],
        help="Fire a specific trigger (respects cooldown)"
    )
    parser.add_argument(
        "--test", choices=["battle_start", "victory"],
        help="Test a trigger (bypasses cooldown)"
    )
    parser.add_argument(
        "--monitor", action="store_true",
        help="Monitor stdin for phase transitions"
    )
    parser.add_argument(
        "--setup", action="store_true",
        help="Download audio and verify installation"
    )
    parser.add_argument(
        "--reset", action="store_true",
        help="Reset state machine (clear cooldowns)"
    )
    parser.add_argument(
        "--status", action="store_true",
        help="Show current state"
    )

    args = parser.parse_args()

    if args.reset:
        reset_state()
        print("✅ State reset.")

    elif args.status:
        state = load_state()
        now = time.time()
        print(f"Phase: {state['phase']}")
        bs_ago = int(now - state.get('last_battle_start', 0))
        v_ago = int(now - state.get('last_victory', 0))
        print(f"Last Battle Start: {bs_ago}s ago (cooldown: {BATTLE_START_COOLDOWN}s)")
        print(f"Last Victory: {v_ago}s ago (cooldown: {VICTORY_COOLDOWN}s)")
        print(f"Can fire Battle Start: {can_fire_battle_start(state)}")
        print(f"Can fire Victory: {can_fire_victory(state)}")

    elif args.trigger == "battle_start":
        fire_battle_start(bypass_cooldown=False)

    elif args.trigger == "victory":
        fire_victory(bypass_cooldown=False)

    elif args.test == "battle_start":
        fire_battle_start(bypass_cooldown=True)

    elif args.test == "victory":
        fire_victory(bypass_cooldown=True)

    elif args.monitor:
        monitor_mode()

    elif args.setup:
        setup_mode()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
