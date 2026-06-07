# PROJECT-detail.md — King Engine Power Skill Shot

## 1. Project Vision

A Claude Skill that turns your coding sessions into anime battle sequences. When the AI agent shifts from "analyzing and planning" to "actually implementing", your machine roars to life with the King Engine heartbeat sound. When the task is done, One Punch Man's OST plays and your terminal explodes with victory effects.

The goal: make AI-assisted coding feel as cinematic and motivating as possible.

---

## 2. The Two Battle Phases

### Phase A: KING ENGINE TRIGGER (Battle Start)
**When:** The agent transitions from analysis/planning/spec into actual implementation work.

**Signals (linguistic markers the agent produces):**
```
IMPLEMENTATION SIGNALS (high confidence):
- "Now I'll implement..."
- "Let me start coding..."
- "I'll now write the code..."
- "Starting implementation..."
- "Let me create the file..."
- "Writing the function..."
- "Here's the implementation:"
- "I'll build this now..."
- bash_tool execution AFTER a planning block
- create_file tool call AFTER analysis text
- str_replace call to write new substantial code

PLANNING COMPLETION SIGNALS (precondition):
- "Here's my plan:" followed by numbered steps
- "I'll approach this by..."
- "First, let me analyze..."
- "The requirements are..." (ends with completion)
- "Here's what I'll do:" (ends with completion)
- str_replace or create_file with substantial content after planning text

PHASE TRANSITION PATTERN:
  [Planning/Analysis block] → [Short bridge phrase] → [Implementation action]
  The KING ENGINE fires at the bridge phrase / first implementation action.
```

**What happens:**
1. `phase_detector.py` identifies transition → signals `BATTLE_START`
2. `king_engine.py` receives signal
3. `audio_player.py` plays `king_engine.mp3` (or fallback beep sequence)
4. `terminal_fx.py` renders the King Engine heartbeat animation
5. Agent continues working while effects play (non-blocking)

### Phase B: VICTORY TRIGGER (Task Complete)
**When:** The agent signals successful task completion.

**Signals:**
```
COMPLETION SIGNALS (high confidence):
- "The task is complete."
- "I've successfully..."
- "Done! Here's what I..."
- "All done."
- "The implementation is complete."
- "Everything is working."
- "I've finished..."
- "The feature is ready."
- "Tests are passing."
- "✅" or "✓" at end of substantial work block

ANTI-SIGNALS (prevent false positives):
- "I'll now complete..." (future tense = not done yet)
- "Next, I'll..." (still in progress)
- "Finally, I need to..." (not done yet)
- Mid-task completion of a sub-step (only fire for overall task completion)
```

**What happens:**
1. `phase_detector.py` identifies completion → signals `VICTORY`
2. `king_engine.py` receives signal
3. `audio_player.py` plays `one_punch_ost.mp3` (or fallback melody)
4. `terminal_fx.py` renders victory sequence
5. Session resets, ready for next task

---

## 3. Terminal Effects Specification

### King Engine Sequence (Battle Start)
```
Duration: ~8 seconds
Style: Dark, intense, building dread

Frame 1 (0.0s):
╔══════════════════════════════════════════╗
║  👑  KING ENGINE ACTIVATED  👑           ║
╚══════════════════════════════════════════╝

Frame 2-N (heartbeat animation):
  💀  D O K I . . .
  💀  D O K I . . .
  💀  D O K I D O K I D O K I D O K I
  ████████████████████████████████████████
  D O K I D O K I D O K I D O K I D O K I
  ████████████████████████████████████████

King ASCII art (shown between heartbeats):

    ╔══════╗
    ║ KING ║
    ║  👑  ║
    ╚══════╝
  ⣿⣿⣿⣿⣿⣿⣿⣿
  THE STRONGEST
   IS ONLINE
   ...implementing

End frame:
⚡ AGENT ENTERING COMBAT MODE ⚡
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
[ KING ENGINE: MAXIMUM OUTPUT ]
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
```

### Victory Sequence (Task Complete)
```
Duration: ~6 seconds
Style: Bright, explosive, triumphant

Frame 1 (instant flash):
★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★

Frame 2:
╔══════════════════════════════════════════╗
║       ⚡  ONE PUUUUNCH!!!  ⚡            ║
╚══════════════════════════════════════════╝

Frame 3 (expanding):
         \  O  /
          |   |    SAITAMA
          / \ \    APPROVED
         MISSION COMPLETE

Frame 4 (Saitama bored face ASCII):
    (  ●  ●  )
    |   ▽   |    "It's done."
    \  ___  /
     \_____/

Frame 5 (explosion):
💥 💥 💥 TASK ANNIHILATED 💥 💥 💥
✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅
  ★ VICTORY ★ VICTORY ★ VICTORY ★
💥 💥 💥 💥 💥 💥 💥 💥 💥 💥 💥 💥
```

---

## 4. Audio Specification

### King Engine Sound
- **Source:** YouTube → `yt-dlp` download, or user provides MP3
- **Alternative:** `beep_sequence.py` generates intimidating low-frequency beep pattern using system beep or `pygame.mixer`
- **Duration:** Loop for 8-10 seconds or until next event
- **Volume:** Medium-high (70% system volume equivalent)

### One Punch Man OST — "THE HERO!! Set Fire to the Furious Fist"
- **Source:** Same approach — user provides or downloads
- **Alternative:** Generate a triumphant 4-note ascending melody via pygame/system
- **Duration:** Play for 15-20 seconds then fade
- **Volume:** Full blast

### Fallback (no audio files, no pygame):
```python
# macOS/Linux: terminal bell + pattern
import os
# King Engine pattern: BOOM...BOOM...BOOM BOOM BOOM BOOM
os.system('echo -e "\\a"')  # terminal bell

# Windows: winsound.Beep(frequency, duration)
import winsound
winsound.Beep(150, 800)  # low thud
```

---

## 5. Phase Detection Algorithm

### Priority Scoring System
Each output chunk is scored for signals:

```python
KING_ENGINE_SIGNALS = {
    # Explicit implementation phrases (score: 10)
    "now i'll implement": 10,
    "let me start coding": 10,
    "i'll now write": 10,
    "starting implementation": 10,
    "writing the": 8,
    "here's the implementation": 10,
    "i'll build": 8,
    "let me create": 7,

    # Tool-based signals (score: 9)
    "bash_tool_after_planning": 9,
    "create_file_call": 9,
    "str_replace_substantial": 8,

    # Planning completion (score: 5 — precondition)
    "here's my plan": 5,
    "i'll approach": 4,
    "the requirements": 3,
}

VICTORY_SIGNALS = {
    # Completion phrases (score: 10)
    "task is complete": 10,
    "i've successfully": 9,
    "all done": 9,
    "implementation is complete": 10,
    "everything is working": 9,
    "i've finished": 8,
    "feature is ready": 9,
    "tests are passing": 9,

    # Anti-signals (negative score — prevent false positives)
    "i'll now complete": -10,
    "next, i'll": -5,
    "finally, i need to": -8,
}

# Threshold to fire:
KING_ENGINE_THRESHOLD = 8
VICTORY_THRESHOLD = 8

# Cooldown: once fired, don't fire again for 60 seconds
BATTLE_START_COOLDOWN = 60
VICTORY_COOLDOWN = 300  # 5 min between victories
```

### State Machine
```
STATES: IDLE → PLANNING → BATTLE_READY → IMPLEMENTING → COMPLETED

IDLE:
  receives planning signals → PLANNING

PLANNING:
  score increases above 5 → BATTLE_READY
  implementation signals → fire KING_ENGINE → IMPLEMENTING

BATTLE_READY:
  any tool call or implementation phrase → fire KING_ENGINE → IMPLEMENTING

IMPLEMENTING:
  victory signals → fire VICTORY → COMPLETED

COMPLETED:
  new task detected → IDLE
```

---

## 6. Integration Guide

### How Claude Agents Use This Skill

The skill runs as a **sidecar process** or **hook system** alongside the agent:

**Option A: Pre/Post Hook** (preferred for Claude Code)
```bash
# In Claude Code hooks configuration:
PreToolUse: python skill/scripts/phase_detector.py --event pre_tool
PostToolUse: python skill/scripts/phase_detector.py --event post_tool
Stop: python skill/scripts/phase_detector.py --event stop
```

**Option B: Standalone Monitor** (for Claude.ai / manual use)
```bash
# Run in a separate terminal alongside your Claude session:
python skill/scripts/king_engine.py --monitor
# Then paste agent output into the monitor's stdin
```

**Option C: Direct Call** (agent calls scripts explicitly per skill instructions)
```bash
# Agent calls at the right moment:
python skill/scripts/king_engine.py --trigger battle_start
python skill/scripts/king_engine.py --trigger victory
```

---

## 7. Setup & Installation

### Prerequisites
```bash
pip install pygame --break-system-packages  # audio playback
pip install yt-dlp --break-system-packages  # audio download (optional)
```

### Audio Download (Optional)
```bash
python skill/scripts/audio_player.py --download-all
# Downloads: king_engine.mp3, one_punch_ost.mp3
# Falls back to generated beeps if download fails
```

### Quick Test
```bash
python skill/scripts/king_engine.py --test battle_start
python skill/scripts/king_engine.py --test victory
```

---

## 8. Edge Cases

| Situation | Handling |
|---|---|
| Agent outputs mid-task completion of sub-step | Anti-signals prevent false VICTORY fire |
| Long implementation with no victory | Victory fires only on explicit completion signal |
| Multiple tasks in one session | State machine resets after each VICTORY |
| No audio hardware | Terminal effects only; audio silently skipped |
| No pygame / afplay | System beep fallback pattern |
| Windows terminal no ANSI | Fallback to plain text mode |
| King Engine fires twice | 60-second cooldown prevents double-fire |
| Agent says "done" casually mid-task | Context scoring + cooldown prevents false trigger |
