#!/usr/bin/env python3
"""
audio_player.py — Cross-Platform Audio Engine
Part of king-engine-power-skill-shot.

Audio playback with 3-tier fallback:
  Tier 1: pygame.mixer (best — works everywhere with MP3 support)
  Tier 2: System command (afplay/paplay/aplay — macOS/Linux)
  Tier 3: System beep pattern (winsound/terminal bell — always works)

Usage:
    python audio_player.py --play king             # Play King Engine audio
    python audio_player.py --play victory          # Play victory audio
    python audio_player.py --test                  # Test all audio
    python audio_player.py --download-all          # Download audio files via yt-dlp
    python audio_player.py --list                  # List available audio files
"""

import sys
import os
import time
import argparse
import subprocess
import threading
from pathlib import Path


ASSETS_DIR = Path(__file__).parent / "assets"

# Audio file definitions
AUDIO_FILES = {
    "king": {
        "filename": "king_engine.mp3",
        "description": "King Engine heartbeat — One Punch Man",
        "duration": 10,  # seconds to play
        "loop": False,
        # YouTube search term for yt-dlp (user must verify copyright compliance)
        "search": "King Engine Sound Effect One Punch Man",
    },
    "victory": {
        "filename": "one_punch_ost.mp3",
        "description": "THE HERO!! Set Fire to the Furious Fist — JAM Project",
        "duration": 20,
        "loop": False,
        "search": "One Punch Man OST THE HERO JAM Project",
    },
}

# Beep fallback patterns (freq_hz, duration_ms)
BEEP_PATTERNS = {
    "king": [
        # Low, intimidating, building — King Engine heartbeat
        (130, 700), (0, 350),   # DOKI...
        (130, 700), (0, 300),   # DOKI...
        (130, 200), (0, 100),   # DOKI
        (130, 200), (0, 100),   # DOKI
        (130, 200), (0, 100),   # DOKI
        (130, 200), (0, 100),   # DOKI
        (160, 300), (0, 100),   # rising
        (180, 500), (0, 200),   # peak
        (200, 800),              # power!
    ],
    "victory": [
        # Triumphant ascending melody — simplified "THE HERO!!"
        (440, 200), (0, 50),    # A
        (494, 200), (0, 50),    # B
        (523, 200), (0, 50),    # C
        (587, 300), (0, 100),   # D
        (659, 300), (0, 100),   # E
        (784, 500), (0, 200),   # G — triumph
        (880, 200), (0, 100),   # A high
        (784, 200), (0, 50),    # G
        (659, 800),              # E sustained — done!
    ],
}


class AudioPlayer:
    """Cross-platform audio player with fallback chain."""

    def __init__(self, assets_dir: Path = None):
        self.assets_dir = assets_dir or ASSETS_DIR
        self.assets_dir.mkdir(parents=True, exist_ok=True)
        self._detect_capabilities()
        self._active_playback = None

    def _detect_capabilities(self):
        """Detect available audio backends."""
        self.has_pygame = False
        self.has_afplay = False  # macOS
        self.has_paplay = False  # Linux (PulseAudio)
        self.has_aplay = False   # Linux (ALSA)
        self.has_mpg123 = False  # Linux
        self.has_winsound = False  # Windows
        self.platform = sys.platform

        try:
            import pygame
            pygame.mixer.init()
            self.has_pygame = True
        except Exception:
            pass

        if self.platform == "darwin":
            self.has_afplay = self._cmd_exists("afplay")
        elif self.platform.startswith("linux"):
            self.has_paplay = self._cmd_exists("paplay")
            self.has_aplay = self._cmd_exists("aplay")
            self.has_mpg123 = self._cmd_exists("mpg123")
        elif self.platform == "win32":
            try:
                import winsound
                self.has_winsound = True
            except ImportError:
                pass

    def _cmd_exists(self, cmd: str) -> bool:
        try:
            subprocess.run(["which", cmd], capture_output=True, check=True)
            return True
        except Exception:
            return False

    def play(self, mode: str, blocking: bool = False):
        """Play audio for the given mode. Non-blocking by default."""
        if blocking:
            self._play_internal(mode)
        else:
            thread = threading.Thread(target=self._play_internal, args=(mode,), daemon=True)
            thread.start()

    def _play_internal(self, mode: str):
        """Internal play logic — tries each tier in order."""
        audio_def = AUDIO_FILES.get(mode, {})
        audio_file = self.assets_dir / audio_def.get("filename", "")
        duration = audio_def.get("duration", 10)

        # Tier 1: pygame (best)
        if self.has_pygame and audio_file.exists():
            try:
                self._play_pygame(str(audio_file), duration)
                return
            except Exception:
                pass

        # Tier 2: system command
        if audio_file.exists():
            try:
                if self.platform == "darwin" and self.has_afplay:
                    proc = subprocess.Popen(
                        ["afplay", str(audio_file)],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                    )
                    time.sleep(min(duration, 15))
                    proc.terminate()
                    return
                elif self.platform.startswith("linux"):
                    for cmd in (
                        ["paplay", str(audio_file)] if self.has_paplay else None,
                        ["mpg123", "-q", str(audio_file)] if self.has_mpg123 else None,
                        ["aplay", str(audio_file)] if self.has_aplay else None,
                    ):
                        if cmd:
                            try:
                                proc = subprocess.Popen(
                                    cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                                )
                                time.sleep(min(duration, 15))
                                proc.terminate()
                                return
                            except Exception:
                                continue
            except Exception:
                pass

        # Tier 3: beep fallback
        self._play_beep(mode)

    def _play_pygame(self, path: str, duration: float):
        import pygame
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
        time.sleep(min(duration, 30))
        pygame.mixer.music.stop()

    def _play_beep(self, mode: str):
        """Generate audio using system beep patterns."""
        pattern = BEEP_PATTERNS.get(mode, [])

        if self.platform == "win32" and self.has_winsound:
            import winsound
            for item in pattern:
                if len(item) == 2:
                    freq, dur = item
                    if freq == 0:
                        time.sleep(dur / 1000)
                    else:
                        winsound.Beep(freq, dur)
        else:
            # Terminal bell pattern (limited but works everywhere)
            for item in pattern[:5]:  # First 5 beeps only
                freq, dur = item
                if freq > 0:
                    sys.stdout.write("\a")
                    sys.stdout.flush()
                time.sleep(dur / 1000)

    def stop(self):
        """Stop current playback."""
        try:
            import pygame
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
        except Exception:
            pass

    def get_status(self) -> dict:
        """Return audio capability status."""
        files_status = {}
        for mode, audio_def in AUDIO_FILES.items():
            audio_file = self.assets_dir / audio_def["filename"]
            files_status[mode] = {
                "file": str(audio_file),
                "exists": audio_file.exists(),
                "size_kb": round(audio_file.stat().st_size / 1024) if audio_file.exists() else 0,
            }

        return {
            "pygame": self.has_pygame,
            "afplay": self.has_afplay,
            "paplay": self.has_paplay,
            "aplay": self.has_aplay,
            "mpg123": self.has_mpg123,
            "winsound": self.has_winsound,
            "platform": self.platform,
            "active_tier": (
                "pygame" if self.has_pygame else
                "system_command" if any([self.has_afplay, self.has_paplay, self.has_aplay]) else
                "beep_fallback"
            ),
            "audio_files": files_status,
        }


def download_audio(mode: str, assets_dir: Path) -> bool:
    """
    Attempt to download audio using yt-dlp.

    NOTE: Users are responsible for ensuring they have the right to download
    and use audio files. This function is a helper only.
    Audio files for personal/non-commercial use only.
    """
    try:
        subprocess.run(["yt-dlp", "--version"], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("⚠️  yt-dlp not installed. Run: pip install yt-dlp --break-system-packages")
        return False

    audio_def = AUDIO_FILES[mode]
    output_path = assets_dir / audio_def["filename"]
    search_query = audio_def["search"]

    print(f"Searching for: {search_query}")
    print(f"Output: {output_path}")
    print("⚠️  Note: For personal use only. Respect copyright.")

    try:
        result = subprocess.run([
            "yt-dlp",
            f"ytsearch1:{search_query}",
            "--extract-audio",
            "--audio-format", "mp3",
            "--audio-quality", "0",
            "-o", str(output_path.with_suffix("")) + ".%(ext)s",
            "--no-playlist",
            "--quiet",
            "--progress",
        ], check=True)
        if output_path.exists():
            print(f"✅ Downloaded: {output_path}")
            return True
        else:
            print(f"⚠️  Download completed but file not found at expected path")
            return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Download failed: {e}")
        return False


# ─── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Audio player for King Engine Power Skill Shot."
    )
    parser.add_argument("--play", choices=["king", "victory"], help="Play audio")
    parser.add_argument("--test", action="store_true", help="Test all audio")
    parser.add_argument("--download-all", action="store_true", help="Download all audio files")
    parser.add_argument("--download", choices=["king", "victory"], help="Download specific audio")
    parser.add_argument("--list", action="store_true", help="List audio files and status")
    parser.add_argument("--assets-dir", type=str, help="Custom assets directory")

    args = parser.parse_args()
    assets_dir = Path(args.assets_dir) if args.assets_dir else ASSETS_DIR
    player = AudioPlayer(assets_dir=assets_dir)

    if args.list:
        status = player.get_status()
        print(f"Platform: {status['platform']}")
        print(f"Active audio tier: {status['active_tier']}")
        print(f"Backends: pygame={status['pygame']}, afplay={status['afplay']}, "
              f"paplay={status['paplay']}, aplay={status['aplay']}")
        print("\nAudio files:")
        for mode, info in status["audio_files"].items():
            icon = "✅" if info["exists"] else "❌"
            print(f"  {icon} [{mode}] {info['file']} ({info['size_kb']}KB)")

    elif args.play:
        print(f"▶️  Playing {args.play}...")
        player.play(args.play, blocking=True)
        print("Done.")

    elif args.test:
        print("🎵 Testing King Engine audio...")
        player.play("king", blocking=True)
        time.sleep(0.5)
        print("🎵 Testing Victory audio...")
        player.play("victory", blocking=True)
        print("✅ Audio test complete.")

    elif args.download_all:
        print("Downloading all audio files...")
        for mode in AUDIO_FILES:
            print(f"\n--- {mode} ---")
            download_audio(mode, assets_dir)

    elif args.download:
        download_audio(args.download, assets_dir)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
