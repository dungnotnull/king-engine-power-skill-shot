#!/usr/bin/env python3
"""
terminal_fx.py — Terminal Animation Engine
Part of king-engine-power-skill-shot.

Renders ANSI terminal animations for King Engine and Victory sequences.

Usage:
    python terminal_fx.py --animate king      # Play King Engine animation
    python terminal_fx.py --animate victory   # Play Victory animation
    python terminal_fx.py --test              # Test both animations
    python terminal_fx.py --preview king      # Preview static frames (no timing)
    python terminal_fx.py --no-clear          # Don't clear screen between frames
"""

import sys
import os
import time
import argparse
import re


# ─── ANSI Codes ────────────────────────────────────────────────────────────────

class A:
    """ANSI escape codes."""
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    BLINK   = "\033[5m"
    REVERSE = "\033[7m"

    BLACK   = "\033[30m"
    RED     = "\033[31m"
    GREEN   = "\033[32m"
    YELLOW  = "\033[33m"
    BLUE    = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN    = "\033[36m"
    WHITE   = "\033[37m"

    BRIGHT_RED    = "\033[91m"
    BRIGHT_GREEN  = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_CYAN   = "\033[96m"
    BRIGHT_WHITE  = "\033[97m"

    BG_BLACK  = "\033[40m"
    BG_RED    = "\033[41m"
    BG_YELLOW = "\033[43m"
    BG_WHITE  = "\033[47m"

    CLEAR = "\033[2J\033[H"
    CLEAR_LINE = "\033[2K\033[G"


def strip_ansi(text: str) -> str:
    """Remove all ANSI escape codes from text."""
    return re.sub(r'\033\[[^m]*m|\033\[2J|\033\[H|\033\[2K|\033\[G', '', text)


def supports_ansi() -> bool:
    """Check if terminal supports ANSI escape codes."""
    if os.environ.get("TERM") == "dumb":
        return False
    if not sys.stdout.isatty():
        return False
    if sys.platform == "win32":
        # Windows 10+ supports ANSI with VT100 mode
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            return True
        except Exception:
            return False
    return True


# ─── King Engine Frames ─────────────────────────────────────────────────────────

def king_engine_frames() -> list[tuple[str, float]]:
    """Return list of (frame_content, hold_seconds) tuples."""
    B = A.BOLD
    Y = A.YELLOW
    BY = A.BOLD + A.BRIGHT_YELLOW
    RD = A.BOLD + A.BRIGHT_RED
    W = A.BOLD + A.WHITE
    DIM = A.DIM + A.WHITE
    R = A.RESET

    return [
        # Frame 0: Warning flash (0.0s)
        (f"{B}{Y}"
         f"\n╔══════════════════════════════════════════════════╗\n"
         f"║                                                  ║\n"
         f"║   👑   K I N G   E N G I N E   O N L I N E  👑  ║\n"
         f"║                                                  ║\n"
         f"╚══════════════════════════════════════════════════╝{R}\n",
         0.7),

        # Frame 1: King ASCII art
        (f"{W}"
         f"\n        ██╗  ██╗██╗███╗   ██╗  ██████╗ \n"
         f"        ██║ ██╔╝██║████╗  ██║ ██╔════╝ \n"
         f"        █████╔╝ ██║██╔██╗ ██║ ██║  ███╗\n"
         f"        ██╔═██╗ ██║██║╚██╗██║ ██║   ██║\n"
         f"        ██║  ██╗██║██║ ╚████║ ╚██████╔╝\n"
         f"        ╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝  ╚═════╝ \n"
         f"{DIM}               S-CLASS HERO  RANK  7{R}\n",
         0.8),

        # Frame 2: First heartbeat — low and slow
        (f"\n{RD}  💀   D  O  K  I  .  .  .{R}\n",
         0.55),

        # Frame 3: Second heartbeat
        (f"\n{RD}  💀   D  O  K  I  .  .  .{R}\n",
         0.5),

        # Frame 4: Faster beat
        (f"\n{RD}{A.BLINK}  💀   D O K I   D O K I   D O K I{R}\n",
         0.35),

        # Frame 5: Full King Engine eruption
        (f"\n{RD}"
         f"████████████████████████████████████████████████████\n"
         f"█                                                  █\n"
         f"█   D O K I  D O K I  D O K I  D O K I  D O K I  █\n"
         f"█                                                  █\n"
         f"████████████████████████████████████████████████████\n"
         f"█   D O K I  D O K I  D O K I  D O K I  D O K I  █\n"
         f"████████████████████████████████████████████████████{R}\n",
         0.6),

        # Frame 6: Inverted flash (aura)
        (f"\n{A.REVERSE}{RD}"
         f"████████████████████████████████████████████████████\n"
         f"█   D O K I  D O K I  D O K I  D O K I  D O K I  █\n"
         f"████████████████████████████████████████████████████{R}\n",
         0.15),

        # Frame 7: Back to normal
        (f"\n{RD}"
         f"████████████████████████████████████████████████████\n"
         f"█   D O K I  D O K I  D O K I  D O K I  D O K I  █\n"
         f"████████████████████████████████████████████████████{R}\n",
         0.15),

        # Frame 8: The fear text
        (f"\n{DIM}"
         f"    ┌─────────────────────────────────────────────────┐\n"
         f"    │  The pressure is unbelievable...               │\n"
         f"    │  Even though he hasn't done a single thing.    │\n"
         f"    └─────────────────────────────────────────────────┘{R}\n",
         1.1),

        # Frame 9: Combat mode banner
        (f"\n{BY}"
         f"  ⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡\n"
         f"  ⚡                                              ⚡\n"
         f"  ⚡    [ AGENT  ENTERING  COMBAT  MODE ]        ⚡\n"
         f"  ⚡    [ KING ENGINE :  MAXIMUM  OUTPUT ]       ⚡\n"
         f"  ⚡    [ ENEMY  ( THE TASK )  IS  DOOMED ]      ⚡\n"
         f"  ⚡                                              ⚡\n"
         f"  ⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡{R}\n",
         1.5),

        # Frame 10: Fade to implementing
        (f"\n{A.DIM}{A.YELLOW}"
         f"  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░\n"
         f"  ░  implementing...                   ░\n"
         f"  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░{R}\n\n",
         0.8),
    ]


# ─── Victory Frames ─────────────────────────────────────────────────────────────

def victory_frames() -> list[tuple[str, float]]:
    """Return victory animation frames."""
    B = A.BOLD
    BY = A.BOLD + A.BRIGHT_YELLOW
    GR = A.BOLD + A.BRIGHT_GREEN
    CY = A.BOLD + A.BRIGHT_CYAN
    RD = A.BOLD + A.BRIGHT_RED
    W = A.BOLD + A.WHITE
    DIM = A.DIM + A.WHITE
    R = A.RESET

    return [
        # Frame V0: Flash burst × 3 rapid
        (f"\n{BY}★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★{R}\n",
         0.12),
        (f"\n{A.REVERSE}{BY}★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★{R}\n",
         0.12),
        (f"\n{BY}★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★{R}\n",
         0.12),

        # Frame V1: ONE PUNCH banner
        (f"\n{CY}"
         f"╔══════════════════════════════════════════════════╗\n"
         f"║                                                  ║\n"
         f"║    ⚡   O N E   P U U U U U N C H ! ! !   ⚡   ║\n"
         f"║                                                  ║\n"
         f"╚══════════════════════════════════════════════════╝{R}\n",
         0.9),

        # Frame V2: Saitama ASCII
        (f"\n{W}"
         f"              ,----,\n"
         f"           ,'      |\n"
         f"     _____/   /|   |\n"
         f"    /      | / |   |          {A.YELLOW}\"Hm.\"{W}\n"
         f"   |       |/  |   |\n"
         f"   |     _/    |   |___\n"
         f"   |    /   ,- |   |* )\n"
         f"   |   /   /   |   /\n"
         f"   `  |   /    |  /\n"
         f"      `  |     | /\n"
         f"        \\|     |/\n"
         f"         `-----'\n"
         f"{DIM}    Saitama — S-Class Rank 1{R}\n",
         1.1),

        # Frame V3: Explosion
        (f"\n{RD}    💥  💥  💥  💥  💥  💥  💥  💥  💥  💥  💥{R}\n",
         0.25),
        (f"\n{GR}"
         f"  ████████████████████████████████████████████████\n"
         f"  █                                              █\n"
         f"  █   ✅   ✅   TASK  ANNIHILATED   ✅   ✅     █\n"
         f"  █                                              █\n"
         f"  ████████████████████████████████████████████████{R}\n",
         0.5),
        (f"\n{RD}    💥  💥  💥  💥  💥  💥  💥  💥  💥  💥  💥{R}\n",
         0.25),

        # Frame V4: Victory scrolling stars
        (f"\n{BY}  ★ VICTORY ★ VICTORY ★ VICTORY ★ VICTORY ★ VICTORY ★{R}\n",
         0.15),
        (f"\n{GR}✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅{R}\n",
         0.15),
        (f"\n{BY}★ VICTORY ★ VICTORY ★ VICTORY ★ VICTORY ★ VICTORY ★ {R}\n",
         0.15),

        # Frame V5: Final score card
        (f"\n{GR}"
         f"  ┌──────────────────────────────────────────────┐\n"
         f"  │                                              │\n"
         f"  │   ✅  MISSION  COMPLETE                     │\n"
         f"  │   ⚡  KING  ENGINE:  POWERED  DOWN         │\n"
         f"  │   🏆  THE  AGENT  HAS  SPOKEN              │\n"
         f"  │   👊  ONE  PUNCH  WAS  ALL  IT  TOOK       │\n"
         f"  │                                              │\n"
         f"  └──────────────────────────────────────────────┘{R}\n",
         2.0),

        # Frame V6: Bored Saitama epilogue
        (f"\n{DIM}"
         f"  (  ●  ●  )    \"...\"\n"
         f"  |   ▽   |    task_complete = True\n"
         f"  \\  ___  /    exit_code = 0\n"
         f"   \\_____/\n{R}\n\n",
         0.8),
    ]


# ─── Renderer ──────────────────────────────────────────────────────────────────

class TerminalFX:
    """Terminal effects renderer."""

    def __init__(self, clear_between_frames: bool = True):
        self.ansi = supports_ansi()
        self.clear_between_frames = clear_between_frames

    def _render_frame(self, content: str, hold: float):
        if self.ansi and self.clear_between_frames:
            sys.stdout.write(A.CLEAR)
        output = content if self.ansi else strip_ansi(content)
        sys.stdout.write(output)
        sys.stdout.flush()
        time.sleep(hold)

    def play_king_engine(self):
        """Play the full King Engine sequence."""
        if self.ansi:
            sys.stdout.write(A.CLEAR)
        for content, hold in king_engine_frames():
            self._render_frame(content, hold)
        if self.ansi:
            sys.stdout.write(A.RESET)
            sys.stdout.flush()

    def play_victory(self):
        """Play the full Victory sequence."""
        if self.ansi:
            sys.stdout.write(A.CLEAR)
        for content, hold in victory_frames():
            self._render_frame(content, hold)
        if self.ansi:
            sys.stdout.write(A.RESET)
            sys.stdout.flush()

    def preview(self, mode: str):
        """Print all frames without delays (for inspection)."""
        frames = king_engine_frames() if mode == "king" else victory_frames()
        for i, (content, hold) in enumerate(frames):
            print(f"\n{'─'*50}")
            print(f"FRAME {i} (hold: {hold}s)")
            print('─'*50)
            output = content if self.ansi else strip_ansi(content)
            print(output)


# ─── Standalone Render (no scripts) ────────────────────────────────────────────

def inline_king_engine():
    """Minimal King Engine effect with no dependencies."""
    fx = TerminalFX(clear_between_frames=False)
    fx.play_king_engine()


def inline_victory():
    """Minimal Victory effect with no dependencies."""
    fx = TerminalFX(clear_between_frames=False)
    fx.play_victory()


# ─── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Terminal FX engine for King Engine Power Skill Shot."
    )
    parser.add_argument("--animate", choices=["king", "victory"],
                        help="Play animation sequence")
    parser.add_argument("--test", action="store_true", help="Test both animations")
    parser.add_argument("--preview", choices=["king", "victory"],
                        help="Preview frames without timing")
    parser.add_argument("--no-clear", action="store_true",
                        help="Don't clear screen between frames")
    parser.add_argument("--no-ansi", action="store_true",
                        help="Force plain text output")

    args = parser.parse_args()
    fx = TerminalFX(clear_between_frames=not args.no_clear)

    if args.no_ansi:
        fx.ansi = False

    if args.animate == "king":
        fx.play_king_engine()

    elif args.animate == "victory":
        fx.play_victory()

    elif args.test:
        print("Testing King Engine...\n")
        fx.play_king_engine()
        time.sleep(0.5)
        print("\nTesting Victory...\n")
        fx.play_victory()
        print("\n✅ Terminal FX test complete.")

    elif args.preview:
        fx.preview(args.preview)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
