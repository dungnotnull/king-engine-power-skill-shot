# Terminal Effects Catalog

_Load this file to render effects manually when scripts are unavailable._
_All ANSI codes work on macOS, Linux, and Windows 10+ terminals._

---

## ANSI Color Reference

```python
RESET   = "\033[0m"
BOLD    = "\033[1m"
DIM     = "\033[2m"
BLINK   = "\033[5m"
REVERSE = "\033[7m"

# Foreground colors
BLACK   = "\033[30m"
RED     = "\033[31m"
GREEN   = "\033[32m"
YELLOW  = "\033[33m"
BLUE    = "\033[34m"
MAGENTA = "\033[35m"
CYAN    = "\033[36m"
WHITE   = "\033[37m"

# Bright variants
BRIGHT_RED    = "\033[91m"
BRIGHT_GREEN  = "\033[92m"
BRIGHT_YELLOW = "\033[93m"
BRIGHT_CYAN   = "\033[96m"
BRIGHT_WHITE  = "\033[97m"

# Background colors
BG_BLACK  = "\033[40m"
BG_RED    = "\033[41m"
BG_YELLOW = "\033[43m"
```

---

## KING ENGINE FRAMES

_Print frames in sequence with `time.sleep()` between each._
_Total duration: ~8 seconds_

### Frame 0 — Screen Clear + Warning (0.0s)
```
[CLEAR SCREEN]

\033[2J\033[H
```

### Frame 1 — Activation Banner (0.0s, hold 0.5s)
```
\033[1m\033[33m
╔══════════════════════════════════════════════════╗
║                                                  ║
║   👑   K I N G   E N G I N E   O N L I N E   👑  ║
║                                                  ║
╚══════════════════════════════════════════════════╝
\033[0m
```

### Frame 2 — King ASCII Art (0.5s, hold 0.8s)
```
\033[1m\033[37m
        ██╗  ██╗██╗███╗   ██╗ ██████╗
        ██║ ██╔╝██║████╗  ██║██╔════╝
        █████╔╝ ██║██╔██╗ ██║██║  ███╗
        ██╔═██╗ ██║██║╚██╗██║██║   ██║
        ██║  ██╗██║██║ ╚████║╚██████╔╝
        ╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝ ╚═════╝
\033[0m
\033[2m\033[37m        S-CLASS HERO RANK 7\033[0m
```

### Frame 3 — First Heartbeat (1.3s)
```
\033[1m\033[31m

  💀  D  O  K  I  .  .  .

\033[0m
```
_Sleep 0.6s_

### Frame 4 — Second Heartbeat (1.9s)
```
\033[1m\033[31m

  💀  D  O  K  I  .  .  .

\033[0m
```
_Sleep 0.5s_

### Frame 5 — Escalating Beat (2.4s)
```
\033[1m\033[31m\033[5m

  💀  D O K I   D O K I   D O K I

\033[0m
```
_Sleep 0.3s_

### Frame 6 — Full King Engine (2.7s, hold 1.0s)
```
\033[1m\033[31m
████████████████████████████████████████████████████
█                                                  █
█   D O K I  D O K I  D O K I  D O K I  D O K I   █
█                                                  █
████████████████████████████████████████████████████
█   D O K I  D O K I  D O K I  D O K I  D O K I   █
████████████████████████████████████████████████████
\033[0m
```

### Frame 7 — Aura Flash (3.7s, 0.1s intervals × 3)
```
[Print Frame 6]  → sleep 0.1s
[Print Frame 7a — inverted colors using \033[7m]  → sleep 0.1s
[Print Frame 6]  → sleep 0.1s
```

### Frame 8 — Pressure Text (4.0s, hold 1.0s)
```
\033[1m\033[37m
    ┌─────────────────────────────────────────────┐
    │  The pressure is unbelievable...            │
    │  Even though he hasn't done a single thing. │
    └─────────────────────────────────────────────┘
\033[0m
```

### Frame 9 — Combat Mode (5.0s, hold 1.5s)
```
\033[1m\033[33m
  ⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡
  ⚡                                            ⚡
  ⚡    [ AGENT ENTERING COMBAT MODE ]          ⚡
  ⚡    [ KING ENGINE : MAXIMUM OUTPUT ]        ⚡
  ⚡    [ ENEMY (THE TASK) IS DOOMED ]         ⚡
  ⚡                                            ⚡
  ⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡
\033[0m
```

### Frame 10 — Fade to Work (6.5s)
```
\033[2m\033[33m
  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
  ░  implementing...                ░
  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
\033[0m
```
_Scroll back to normal — agent continues work_

---

## VICTORY FRAMES

_Total duration: ~6 seconds_

### Frame V0 — Flash (0.0s, 0.05s intervals × 5)
```python
# Alternate between these two rapidly:
"\033[1m\033[43m\033[30m★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★\033[0m"
"\033[1m\033[33m★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★\033[0m"
```

### Frame V1 — ONE PUNCH Banner (0.25s, hold 0.8s)
```
\033[1m\033[93m
╔══════════════════════════════════════════════════╗
║                                                  ║
║        ⚡  O N E   P U U U U U N C H ! ! !  ⚡   ║
║                                                  ║
╚══════════════════════════════════════════════════╝
\033[0m
```

### Frame V2 — Saitama ASCII (1.05s, hold 1.0s)
```
\033[1m\033[97m
              ,----,
           ,'     |
     _____/  /|   |          \033[33m "Hm."
    /     | / |   |
   |      |/  |   |___
   |    _/    |   | * )
   |   /   ,- |   |/
   `  |   /   |   /
      `  |    |  /
        \|    | /
         `----'
\033[0m
\033[2m\033[37m       Saitama, S-Class Hero Rank 1\033[0m
```

### Frame V3 — Explosion (2.05s, hold 0.8s)
```
\033[1m\033[91m
    💥  💥  💥  💥  💥  💥  💥  💥  💥  💥
\033[0m
\033[1m\033[92m
  ████████████████████████████████████████████████
  █                                              █
  █   ✅  ✅  TASK ANNIHILATED  ✅  ✅           █
  █                                              █
  ████████████████████████████████████████████████
\033[0m
\033[1m\033[91m
    💥  💥  💥  💥  💥  💥  💥  💥  💥  💥
\033[0m
```

### Frame V4 — Victory Stars (2.85s, animated × 3 passes)
```
# Each pass shifts the pattern:
Pass 1: \033[1m\033[93m  ★ VICTORY ★ VICTORY ★ VICTORY ★ VICTORY ★\033[0m
Pass 2: \033[1m\033[97m★ VICTORY ★ VICTORY ★ VICTORY ★ VICTORY ★ \033[0m
Pass 3: \033[1m\033[93m ★ VICTORY ★ VICTORY ★ VICTORY ★ VICTORY ★ \033[0m
# Sleep 0.12s between passes
```

### Frame V5 — Final Score (3.2s, hold 2.0s)
```
\033[1m\033[92m
  ┌────────────────────────────────────────────────┐
  │                                                │
  │   ✅  MISSION COMPLETE                         │
  │   ⚡  KING ENGINE: POWERED DOWN               │
  │   🏆  THE AGENT HAS SPOKEN                    │
  │   👊  ONE PUNCH WAS ALL IT TOOK               │
  │                                                │
  └────────────────────────────────────────────────┘
\033[0m
```

### Frame V6 — Bored Saitama (5.2s, hold 0.8s)
```
\033[2m\033[37m
  (  ●  ●  )   "..."
  |   ▽   |
  \  ___  /    task_complete = True
   \_____/
\033[0m
```
_Fade out. Return to normal terminal._

---

## Fallback: No ANSI Support (Plain Text Mode)

Detect with: `os.environ.get('TERM') == 'dumb'` or `not sys.stdout.isatty()`

### King Engine Plain Text
```
==================================================
  KING ENGINE ACTIVATED
  D O K I   D O K I   D O K I   D O K I
  [ AGENT ENTERING COMBAT MODE ]
==================================================
```

### Victory Plain Text
```
==================================================
  ONE PUUUUNCH!!!
  TASK COMPLETE - MISSION ACCOMPLISHED
  ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅
==================================================
```

---

## Render Loop Template

```python
import sys, time

def render_frames(frames: list[tuple[str, float]], ansi: bool = True):
    """
    frames: list of (content_str, hold_seconds)
    """
    for content, hold in frames:
        if ansi:
            sys.stdout.write("\033[2J\033[H")  # clear screen
        sys.stdout.write(content + "\n")
        sys.stdout.flush()
        time.sleep(hold)
    if ansi:
        sys.stdout.write("\033[0m")  # reset colors
        sys.stdout.flush()
```
