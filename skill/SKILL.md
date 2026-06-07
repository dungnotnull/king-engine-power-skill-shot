---
name: king-engine-power-skill-shot
description: ACTIVATE when an AI coding agent is about to transition from planning/analysis into actual implementation, OR when it successfully completes a task. This skill fires the King Engine heartbeat sound effect + terminal animation at battle start (One Punch Man's King character), and the One Punch Man victory OST + terminal celebration on task completion. Use this skill whenever you are: about to start implementing after analyzing requirements, about to write code after writing specs or a plan, just finished a task successfully, or completing a significant coding milestone. This is a motivational battle system — always trigger it at the right dramatic moment for maximum cinematic impact. The skill enhances the coding experience with sound + terminal effects. Trigger KING_ENGINE when transitioning plan→code. Trigger VICTORY when task is done.
---

# 👑 KING ENGINE POWER SKILL SHOT ⚡

*"The pressure in the atmosphere is unbelievable... even though he hasn't done a single thing."*

You are the King of the coding arena. This skill fires at two critical dramatic moments:
- **KING ENGINE** — when you shift from planning into actual implementation
- **VICTORY** — when you successfully complete the task

---

## WHEN TO FIRE KING ENGINE (Battle Start)

Fire immediately when **ALL** of these are true:
1. You have finished analyzing the requirements, reading specs, or planning your approach
2. You are about to write actual code, create files, or execute implementation commands
3. You have NOT already fired King Engine in the last 60 seconds for this task

**Trigger phrase patterns that indicate this moment:**
- You are about to say "Now I'll implement...", "Let me start coding...", "Here's the implementation:"
- You are about to make a `bash_tool` call that actually builds/runs something (not just reads)
- You are about to call `create_file` or `str_replace` with substantial code content
- You just finished outlining a plan and are about to execute it

**Protocol — run this in sequence (non-blocking):**
```bash
python skill/scripts/king_engine.py --trigger battle_start &
```

If scripts are unavailable, render the terminal sequence manually:
→ Load `references/terminal-effects-catalog.md` → Section "KING ENGINE FRAMES"
→ Print frames with stated delays

---

## WHEN TO FIRE VICTORY

Fire immediately when **ALL** of these are true:
1. The main task is fully complete — not just a sub-step
2. You are saying something that signals completion ("done", "complete", "finished", "working", "all tests pass")
3. You have NOT already fired Victory for this task

**Do NOT fire Victory for:**
- Completing a single sub-step ("I've finished the function, now let me...")
- Saying "done" in the middle of a multi-step task
- Future-tense completion ("this will complete the feature")

**Protocol — run this in sequence:**
```bash
python skill/scripts/king_engine.py --trigger victory &
```

If scripts unavailable:
→ Load `references/terminal-effects-catalog.md` → Section "VICTORY FRAMES"
→ Print frames with stated delays

---

## INTEGRATION MODES

### Mode 1: Claude Code (Recommended — Hooks)
Add to your Claude Code hooks (`.claude/settings.json`):
```json
{
  "hooks": {
    "PreToolUse": "python /path/to/skill/scripts/phase_detector.py --event pre_tool",
    "PostToolUse": "python /path/to/skill/scripts/phase_detector.py --event post_tool",
    "Stop": "python /path/to/skill/scripts/phase_detector.py --event stop"
  }
}
```
The hooks auto-detect phases and fire effects without any manual triggering.

### Mode 2: Direct Agent Call (This SKILL.md approach)
The agent follows the protocols above and calls `king_engine.py --trigger` at the right moments.

### Mode 3: Terminal Monitor (Claude.ai / any interface)
```bash
# Run in a separate terminal:
python skill/scripts/king_engine.py --monitor
```
Reads stdin for agent output and auto-detects phases.

---

## SCRIPT QUICK REFERENCE

| Script | Purpose | Key Args |
|---|---|---|
| `king_engine.py` | Main orchestrator | `--trigger battle_start/victory`, `--test`, `--monitor` |
| `phase_detector.py` | Phase detection engine | `--event pre_tool/post_tool/stop`, `--text "..."` |
| `audio_player.py` | Cross-platform audio | `--play king/victory`, `--download-all`, `--test` |
| `terminal_fx.py` | Terminal animations | `--animate king/victory`, `--test` |

---

## SETUP (First Time)
```bash
pip install pygame --break-system-packages   # audio (optional but recommended)
python skill/scripts/king_engine.py --setup  # download audio, test effects
```

---

## REFERENCE FILES
| File | Load When |
|---|---|
| `references/phase-detection-guide.md` | Debugging phase detection, tuning signals |
| `references/terminal-effects-catalog.md` | Rendering effects without scripts |

---

## THE PHILOSOPHY

King won every battle by doing absolutely nothing — his legend did the work.
Your agent is King. The King Engine plays. The enemy (the task) trembles.
Then: ONE PUNCH. Done.

*DOKI DOKI DOKI DOKI DOKI DOKI DOKI DOKI*
