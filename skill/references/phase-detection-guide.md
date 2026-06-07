# Phase Detection Guide

_Reference for king-engine-power-skill-shot. Load when debugging phase detection or tuning signals._

---

## State Machine

```
IDLE ──────► PLANNING ──────► BATTLE_READY ──────► IMPLEMENTING ──────► COMPLETED
  ▲                                │                                          │
  └──────────────────────────────────────────────────────────── reset ◄───────┘
```

### State Transitions

| From | Signal | To | Action |
|---|---|---|---|
| IDLE | Any planning signal (score ≥ 3) | PLANNING | — |
| PLANNING | Implementation signal (score ≥ 8) | IMPLEMENTING | 🔥 FIRE KING ENGINE |
| PLANNING | Plan completion + tool call | IMPLEMENTING | 🔥 FIRE KING ENGINE |
| BATTLE_READY | Any tool call | IMPLEMENTING | 🔥 FIRE KING ENGINE |
| IMPLEMENTING | Victory signal (score ≥ 8) | COMPLETED | 🏆 FIRE VICTORY |
| COMPLETED | New task keyword | IDLE | Reset cooldowns |

---

## King Engine Signal Dictionary

### HIGH CONFIDENCE — Implementation Start (score 10)
```
"now i'll implement"
"let me start coding"
"i'll now write the code"
"starting implementation"
"here's the implementation"
"i'll implement this"
"time to code"
"let me code this up"
"i'll now create"
"writing the code now"
```

### MEDIUM CONFIDENCE — Likely Implementation (score 7–9)
```
"let me write"            (8)
"i'll create the file"    (8)
"writing the function"    (7)
"here's the code"         (8)
"i'll build this"         (7)
"let me add"              (6)
"adding the"              (5)
"implementing"            (7)
"coding this"             (8)
"creating the"            (6)
```

### TOOL-BASED SIGNALS (score varies)
```
bash_tool called with: make, npm, pip, cargo, go build, python, node    → 9
bash_tool called with: mkdir, touch, mv, cp (after planning block)      → 8
create_file called with code content (>50 chars body)                    → 9
str_replace called with substantial new code block                       → 8
bash_tool called with: cat, ls, echo (just reading)                     → 2
```

### PLANNING SIGNALS (precondition only, score 3–5)
```
"here's my plan"          (5)
"i'll approach this"      (4)
"the requirements are"    (3)
"let me analyze"          (3)
"i need to"               (2)
"first, i'll"             (3)
"my approach will be"     (4)
"the plan is"             (5)
```

---

## Victory Signal Dictionary

### HIGH CONFIDENCE — Task Complete (score 10)
```
"the task is complete"
"i've successfully completed"
"all done!"
"implementation is complete"
"everything is working"
"the feature is ready"
"all tests are passing"
"mission accomplished"
"task complete"
"done! ✅"
"✅ complete"
```

### MEDIUM CONFIDENCE (score 7–9)
```
"i've finished"           (8)
"finished!"               (7)
"that's done"             (7)
"it's working"            (8)
"this should work"        (6)
"successfully implemented" (9)
"the code is ready"       (8)
"all good"                (6)
```

### ANTI-SIGNALS — Prevent False Positives (score −5 to −10)
```
"i'll now complete"       (−10) ← future tense, not done yet
"next, i'll"              (−8)  ← still in progress
"finally, i need to"      (−8)  ← final step upcoming
"then i'll"               (−6)  ← continuing
"after this"              (−5)  ← more steps coming
"now let me"              (−5)  ← transitioning between steps
"the next step"           (−8)  ← not done
"i still need to"         (−10) ← explicitly not done
"almost done"             (−6)  ← not done
"one more thing"          (−8)  ← not done
```

### CONTEXT FILTERS
```
# Only fire Victory if:
# 1. Total positive score ≥ 8
# 2. No anti-signals cancel it below threshold
# 3. We are in IMPLEMENTING state (had a King Engine first)
#    OR this is a clearly complete short task
# 4. Victory cooldown not active (5 min since last victory)
# 5. The completion refers to the MAIN task, not a subtask
#    (heuristic: if followed by "now let me...", it's a subtask)
```

---

## False Positive Scenarios & Countermeasures

### Scenario 1: Casual "done" mid-task
```
Agent: "I've added the login function. Now let me work on logout..."
```
**Problem:** "I've added" matches victory signals
**Countermeasure:** "Now let me" anti-signal cancels it

### Scenario 2: Planning uses implementation words
```
Agent: "I'll implement this by first analyzing the codebase..."
```
**Problem:** "I'll implement" matches King Engine signal
**Countermeasure:** "first analyzing" → still in planning, score drops below threshold

### Scenario 3: King Engine re-fires mid-implementation
```
Agent: "Now I'll write the second function..."
```
**Problem:** Re-triggers during ongoing implementation
**Countermeasure:** 60-second cooldown. IMPLEMENTING state suppresses re-trigger.

### Scenario 4: Victory fires on sub-step
```
Agent: "The database schema is complete. Now I'll write the API routes."
```
**Problem:** "complete" triggers victory
**Countermeasure:** "Now I'll" anti-signal + state machine knows task continues

### Scenario 5: Code comments contain trigger words
```python
# Implementation complete - add tests next
def some_function():
```
**Problem:** Comment contains "implementation complete"
**Countermeasure:** Lines starting with `#` or `//` are excluded from scoring

---

## Hook Integration (Claude Code)

### PreToolUse Hook
Receives: tool name + input
```json
{
  "tool": "bash_tool",
  "input": {"command": "npm run build"}
}
```
Detection logic:
- `bash_tool` with build/run commands after planning state → King Engine signal
- `create_file` with code content → King Engine signal
- `bash_tool` with `cat`/`ls` → low signal (reading)

### PostToolUse Hook
Receives: tool name + output
```json
{
  "tool": "bash_tool",
  "output": {"stdout": "✓ All tests passed\n✓ Build successful"}
}
```
Detection logic:
- Success output from test runner → Victory signal boost
- Build success → Victory signal boost
- Error output → suppress Victory

### Stop Hook
Fires when agent stops (task complete or waiting).
- Check accumulated signals: if IMPLEMENTING state → Victory check
- If score ≥ 8 → fire Victory

---

## Tuning Parameters

Adjust in `phase_detector.py`:

```python
# Signal thresholds
KING_ENGINE_THRESHOLD = 8    # Lower = more sensitive (more triggers)
VICTORY_THRESHOLD = 8        # Lower = more sensitive (more victories)

# Cooldowns
BATTLE_START_COOLDOWN = 60   # seconds — prevent double-fire
VICTORY_COOLDOWN = 300       # seconds — 5 min between victories

# Context window for signal scoring
SCORING_WINDOW_CHARS = 500   # Only score last N characters of output

# Planning phase minimum duration before King Engine can fire
MIN_PLANNING_SCORE = 5       # Must have seen planning signals first
```
