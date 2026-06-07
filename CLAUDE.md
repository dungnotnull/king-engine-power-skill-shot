# KING ENGINE POWER SKILL SHOT ⚡👑
### *"The strongest man on Earth... is your laptop"*

---

## What This Project Does

This skill is a **motivational battle system** for AI coding agents, inspired by King — the S-Class Hero Rank 7 from One Punch Man who is secretly the weakest hero, but whose legend (the "King Engine" heartbeat) terrifies every enemy into submission.

The skill monitors the AI agent's workflow phases and fires two cinematic audio+terminal moments:

| Trigger | Audio | Terminal Effect |
|---|---|---|
| **BATTLE START** — agent finishes analysis/spec and begins implementation | King Engine sound (intimidating heartbeat) | Dramatic DOKI DOKI heartbeat animation |
| **VICTORY** — agent successfully completes the task | One Punch Man OST "THE HERO!!" | Epic victory terminal animation |

## Why This Exists

Because coding with an AI agent should feel like being King: outwardly terrifying, secretly panicking, somehow winning every time.

## Repository Structure

```
king-engine-power-skill-shot/
├── CLAUDE.md                              ← You are here
├── PROJECT-detail.md                      ← Full spec
├── PROJECT-DEVELOPMENT-PHASE-TRACKING.md  ← Phase tracker
├── README.md                              ← Install & usage
├── skill/
│   ├── SKILL.md                           ← Main skill harness
│   ├── references/
│   │   ├── phase-detection-guide.md       ← How to detect workflow phases
│   │   └── terminal-effects-catalog.md    ← All ASCII animations & text effects
│   ├── scripts/
│   │   ├── king_engine.py                 ← Main orchestrator script
│   │   ├── phase_detector.py              ← Phase detection logic
│   │   ├── audio_player.py                ← Cross-platform audio engine
│   │   ├── terminal_fx.py                 ← Terminal animation engine
│   │   └── assets/
│   │       ├── king_engine.mp3            ← King Engine heartbeat SFX (downloaded)
│   │       └── one_punch_ost.mp3          ← "THE HERO!!" OST (downloaded)
│   └── assets/
│       └── ascii_art.txt                  ← King ASCII art + Saitama art
└── evals/
    └── evals.json                         ← Phase detection test cases
```

## Core Technical Challenge

The hard part is **accurate phase detection** — knowing EXACTLY when:
1. The agent transitions from planning → implementation (King Engine trigger)
2. The agent signals successful task completion (Victory trigger)

This is solved via `phase_detector.py` which scans agent output for linguistic and structural signals.

## Platform Support

| Platform | Audio | Terminal FX |
|---|---|---|
| macOS | `afplay` (built-in) | Full ANSI support |
| Linux | `aplay` / `paplay` (usually installed) | Full ANSI support |
| Windows | `winsound` / PowerShell | Full ANSI support (Win10+) |
| All | `pygame` fallback | Always works |
