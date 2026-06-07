#!/usr/bin/env python3
"""
phase_detector.py — Phase Detection Engine
Part of king-engine-power-skill-shot.

Detects when the AI agent transitions between:
  IDLE → PLANNING → IMPLEMENTING (fires KING ENGINE)
  IMPLEMENTING → COMPLETED (fires VICTORY)

Usage:
    # Claude Code hook mode:
    python phase_detector.py --event pre_tool --tool bash_tool --input '{"command":"npm build"}'
    python phase_detector.py --event post_tool --tool bash_tool --output '{"stdout":"Tests passed"}'
    python phase_detector.py --event stop

    # Text analysis mode:
    python phase_detector.py --text "Now I'll implement the feature..."
    echo "Task complete!" | python phase_detector.py --stdin

    # Interactive monitor:
    python phase_detector.py --monitor

Output:
    JSON: {"event": "BATTLE_START" | "VICTORY" | "NONE", "score": int, "state": str}
"""

import sys
import json
import re
import time
import argparse
from pathlib import Path


# ─── Signal Dictionaries ────────────────────────────────────────────────────────

KING_ENGINE_SIGNALS: dict[str, int] = {
    # Explicit implementation phrases
    "now i'll implement": 10,
    "let me start coding": 10,
    "i'll now write the code": 10,
    "starting implementation": 10,
    "here's the implementation": 10,
    "i'll implement this": 10,
    "time to code": 9,
    "let me code this up": 10,
    "i'll now create": 9,
    "writing the code now": 10,
    "let me write": 8,
    "i'll create the file": 8,
    "writing the function": 7,
    "here's the code": 8,
    "i'll build this": 7,
    "implementing": 7,
    "coding this": 8,
    "let me now": 6,
    "i'll now": 7,
    "now let me write": 9,
    "starting to write": 8,
    "begin implementation": 10,
    "start implementing": 10,
    "ready to implement": 9,
}

VICTORY_SIGNALS: dict[str, int] = {
    # Completion phrases
    "the task is complete": 10,
    "i've successfully completed": 10,
    "all done": 9,
    "implementation is complete": 10,
    "everything is working": 9,
    "the feature is ready": 9,
    "all tests are passing": 9,
    "tests are passing": 9,
    "mission accomplished": 10,
    "task complete": 9,
    "i've finished": 8,
    "finished!": 7,
    "that's done": 7,
    "it's working": 8,
    "successfully implemented": 9,
    "the code is ready": 8,
    "done!": 7,
    "complete!": 7,
    "and it's done": 9,
    "implementation complete": 10,
    "the implementation is done": 10,
    "i've completed": 8,
    "successfully created": 8,
    "successfully built": 9,
    "build successful": 9,
    "all tests passed": 10,
    "✅ done": 10,
    "✅ complete": 10,
    "task accomplished": 10,
}

VICTORY_ANTI_SIGNALS: dict[str, int] = {
    # Future tense / still in progress
    "i'll now complete": -10,
    "next, i'll": -8,
    "finally, i need to": -8,
    "then i'll": -6,
    "after this": -5,
    "now let me": -5,
    "the next step": -8,
    "i still need to": -10,
    "almost done": -6,
    "one more thing": -8,
    "i'll also": -6,
    "additionally": -4,
    "furthermore": -4,
    "next i'll": -8,
    "and then": -5,
    "but first": -7,
}

PLANNING_SIGNALS: dict[str, int] = {
    "here's my plan": 5,
    "i'll approach": 4,
    "the requirements are": 3,
    "let me analyze": 3,
    "i need to": 2,
    "first, i'll": 3,
    "my approach will be": 4,
    "the plan is": 5,
    "let me think": 3,
    "analyzing": 3,
    "let me review": 3,
    "understanding the": 2,
    "reading the": 2,
    "the goal is": 3,
    "i'll start by": 4,
    "to accomplish this": 4,
    "my strategy": 4,
    "before implementing": 5,
    "before writing": 5,
}

# Tools that strongly signal implementation (when called after planning)
IMPLEMENTATION_TOOLS = {
    "bash_tool": {
        # Commands that indicate implementation
        "impl_cmds": ["npm", "pip", "cargo", "go build", "make", "python", "node",
                      "jest", "pytest", "mkdir", "touch", "git commit", "docker"],
        # Commands that indicate just reading
        "read_cmds": ["cat", "ls", "echo", "pwd", "head", "tail", "grep", "find",
                      "which", "env", "printenv"],
        "impl_score": 9,
        "read_score": 2,
    },
    "create_file": {"impl_score": 9},
    "str_replace": {"impl_score": 8},
    "write_file": {"impl_score": 9},
}

# Success signals from tool output
VICTORY_TOOL_OUTPUT_SIGNALS = {
    "all tests passed": 10,
    "tests passed": 9,
    "build successful": 9,
    "build succeeded": 9,
    "✓": 3,
    "✅": 5,
    "success": 5,
    "passing": 6,
    "compiled successfully": 9,
    "done.": 5,
}

# Failure signals (prevent Victory on error)
FAILURE_TOOL_OUTPUT_SIGNALS = {
    "error": -8,
    "failed": -8,
    "failure": -8,
    "exception": -6,
    "traceback": -8,
    "segfault": -8,
    "syntax error": -8,
    "test failed": -10,
    "build failed": -10,
}


# ─── State Machine ──────────────────────────────────────────────────────────────

STATES = ["IDLE", "PLANNING", "BATTLE_READY", "IMPLEMENTING", "COMPLETED"]

STATE_FILE = Path("/tmp/king_engine_state.json")

KING_ENGINE_THRESHOLD = 8
VICTORY_THRESHOLD = 8
PLANNING_THRESHOLD = 5


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return {"phase": "IDLE", "planning_score": 0, "last_battle": 0, "last_victory": 0}


def save_state(state: dict):
    try:
        STATE_FILE.write_text(json.dumps(state))
    except Exception:
        pass


# ─── Text Scoring ───────────────────────────────────────────────────────────────

def normalize(text: str) -> str:
    """Normalize text for matching."""
    return re.sub(r'\s+', ' ', text.lower().strip())


def score_text(text: str, signals: dict[str, int]) -> tuple[int, list[str]]:
    """Score text against a signal dictionary. Returns (score, matched_signals)."""
    normalized = normalize(text)
    total = 0
    matched = []

    # Skip commented lines (code comments)
    lines = [l for l in text.split('\n')
             if not l.strip().startswith(('#', '//', '--', '/*', '*'))]
    clean_text = normalize(' '.join(lines))

    for phrase, score in signals.items():
        if phrase in clean_text:
            total += score
            matched.append(f"{phrase}({score:+d})")

    return total, matched


def score_king_engine(text: str) -> tuple[int, list[str]]:
    score, matched = score_text(text, KING_ENGINE_SIGNALS)
    return score, matched


def score_victory(text: str) -> tuple[int, list[str]]:
    pos_score, pos_matched = score_text(text, VICTORY_SIGNALS)
    neg_score, neg_matched = score_text(text, VICTORY_ANTI_SIGNALS)
    total = pos_score + neg_score  # neg_score is already negative
    return total, pos_matched + neg_matched


def score_planning(text: str) -> tuple[int, list[str]]:
    return score_text(text, PLANNING_SIGNALS)


def score_tool(tool_name: str, tool_input: dict = None, tool_output: dict = None) -> tuple[int, str]:
    """Score a tool call for phase detection."""
    score = 0
    signal = "none"

    if tool_name in IMPLEMENTATION_TOOLS:
        tool_def = IMPLEMENTATION_TOOLS[tool_name]

        if tool_name == "bash_tool" and tool_input:
            cmd = str(tool_input.get("command", "")).lower()
            is_impl = any(ic in cmd for ic in tool_def["impl_cmds"])
            is_read = any(rc in cmd for rc in tool_def["read_cmds"])

            if is_impl:
                score = tool_def["impl_score"]
                signal = f"bash({cmd[:30]}...)"
            elif is_read:
                score = tool_def["read_score"]
                signal = f"bash_read({cmd[:20]})"
            else:
                score = 5  # unknown bash command — moderate signal
                signal = f"bash_unknown({cmd[:20]})"

        elif tool_name in ("create_file", "write_file", "str_replace"):
            score = tool_def["impl_score"]
            signal = tool_name

        # Score output (for victory detection)
        if tool_output:
            output_str = normalize(str(tool_output))
            for sig, s in VICTORY_TOOL_OUTPUT_SIGNALS.items():
                if sig in output_str:
                    score += s
                    signal += f"+output({sig})"
                    break
            for sig, s in FAILURE_TOOL_OUTPUT_SIGNALS.items():
                if sig in output_str:
                    score += s  # negative
                    signal += f"+fail({sig})"
                    break

    return score, signal


# ─── Phase Detector Class ───────────────────────────────────────────────────────

class PhaseDetector:
    """Stateful phase detector. Processes text or tool events."""

    BATTLE_COOLDOWN = 60
    VICTORY_COOLDOWN = 300

    def __init__(self):
        self.state = load_state()

    def process_text(self, text: str) -> str:
        """Process a text chunk. Returns 'BATTLE_START', 'VICTORY', or 'NONE'."""
        state = self.state
        now = time.time()

        # Score the text
        ke_score, ke_matched = score_king_engine(text)
        v_score, v_matched = score_victory(text)
        p_score, p_matched = score_planning(text)

        result = "NONE"

        phase = state.get("phase", "IDLE")

        # Update planning score accumulator
        if p_score > 0:
            state["planning_score"] = state.get("planning_score", 0) + p_score

        # State machine transitions
        if phase in ("IDLE", "PLANNING"):
            if p_score > 0:
                state["phase"] = "PLANNING"

            # Check for King Engine trigger
            if ke_score >= KING_ENGINE_THRESHOLD:
                cool_ok = (now - state.get("last_battle", 0)) > self.BATTLE_COOLDOWN
                if cool_ok:
                    state["phase"] = "IMPLEMENTING"
                    state["last_battle"] = now
                    state["planning_score"] = 0
                    result = "BATTLE_START"

        elif phase == "IMPLEMENTING":
            # Check for Victory trigger
            if v_score >= VICTORY_THRESHOLD:
                cool_ok = (now - state.get("last_victory", 0)) > self.VICTORY_COOLDOWN
                if cool_ok:
                    state["phase"] = "COMPLETED"
                    state["last_victory"] = now
                    result = "VICTORY"

        elif phase == "COMPLETED":
            # Reset on new task signals
            new_task_signals = ["new task", "next task", "another task", "can you", "please"]
            if any(sig in normalize(text) for sig in new_task_signals):
                state["phase"] = "IDLE"
                state["planning_score"] = 0

        self.state = state
        save_state(state)
        return result

    def process_tool_event(self, event: str, tool_name: str = "",
                           tool_input: dict = None, tool_output: dict = None) -> str:
        """Process a Claude Code hook event."""
        state = self.state
        now = time.time()
        phase = state.get("phase", "IDLE")

        tool_score, tool_signal = score_tool(tool_name, tool_input, tool_output)
        result = "NONE"

        if event == "pre_tool":
            # PreToolUse: detect implementation start
            if tool_score >= KING_ENGINE_THRESHOLD:
                if phase in ("IDLE", "PLANNING", "BATTLE_READY"):
                    cool_ok = (now - state.get("last_battle", 0)) > self.BATTLE_COOLDOWN
                    if cool_ok:
                        state["phase"] = "IMPLEMENTING"
                        state["last_battle"] = now
                        result = "BATTLE_START"

        elif event == "post_tool":
            # PostToolUse: detect victory from successful output
            if tool_score >= VICTORY_THRESHOLD and phase == "IMPLEMENTING":
                cool_ok = (now - state.get("last_victory", 0)) > self.VICTORY_COOLDOWN
                if cool_ok:
                    state["phase"] = "COMPLETED"
                    state["last_victory"] = now
                    result = "VICTORY"

        elif event == "stop":
            # Agent stopped — check if it's done
            if phase == "IMPLEMENTING":
                # Assume task is done when agent stops voluntarily
                cool_ok = (now - state.get("last_victory", 0)) > self.VICTORY_COOLDOWN
                if cool_ok:
                    state["phase"] = "COMPLETED"
                    state["last_victory"] = now
                    result = "VICTORY"
            state["phase"] = "IDLE"
            state["planning_score"] = 0

        self.state = state
        save_state(state)
        return result

    def process_line(self, line: str) -> str:
        """Process a single line (for monitor mode)."""
        return self.process_text(line)


# ─── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Phase detector for King Engine skill.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--event", choices=["pre_tool", "post_tool", "stop"],
                       help="Claude Code hook event type")
    group.add_argument("--text", type=str, help="Analyze a text snippet")
    group.add_argument("--stdin", action="store_true", help="Read text from stdin")
    group.add_argument("--monitor", action="store_true", help="Interactive monitor mode")
    group.add_argument("--status", action="store_true", help="Show current state")

    parser.add_argument("--tool", type=str, default="", help="Tool name (for hook events)")
    parser.add_argument("--input", type=str, default="{}", help="Tool input JSON")
    parser.add_argument("--output", type=str, default="{}", help="Tool output JSON")
    parser.add_argument("--pretty", action="store_true", help="Pretty print JSON output")
    parser.add_argument("--fire", action="store_true",
                        help="Auto-fire king_engine.py when phase detected")

    args = parser.parse_args()
    detector = PhaseDetector()

    def fire_if_needed(event: str):
        if args.fire and event != "NONE":
            import subprocess
            script = Path(__file__).parent / "king_engine.py"
            trigger = "battle_start" if event == "BATTLE_START" else "victory"
            subprocess.Popen(
                [sys.executable, str(script), "--trigger", trigger],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )

    if args.status:
        state = load_state()
        print(json.dumps(state, indent=2))

    elif args.event:
        try:
            tool_input = json.loads(args.input)
            tool_output = json.loads(args.output)
        except json.JSONDecodeError:
            tool_input, tool_output = {}, {}

        result = detector.process_tool_event(
            args.event, args.tool, tool_input, tool_output
        )
        output = {
            "event": result,
            "state": detector.state.get("phase"),
            "tool": args.tool,
        }
        indent = 2 if args.pretty else None
        print(json.dumps(output, indent=indent))
        fire_if_needed(result)

    elif args.text:
        result = detector.process_text(args.text)
        ke_score, ke_matched = score_king_engine(args.text)
        v_score, v_matched = score_victory(args.text)
        output = {
            "event": result,
            "state": detector.state.get("phase"),
            "king_engine_score": ke_score,
            "victory_score": v_score,
            "king_engine_signals": ke_matched,
            "victory_signals": v_matched,
        }
        indent = 2 if args.pretty else None
        print(json.dumps(output, indent=indent))
        fire_if_needed(result)

    elif args.stdin:
        text = sys.stdin.read()
        result = detector.process_text(text)
        print(json.dumps({"event": result, "state": detector.state.get("phase")}))
        fire_if_needed(result)

    elif args.monitor:
        print("[Phase Detector] 👁 Monitoring stdin — paste agent output below:", file=sys.stderr)
        for line in sys.stdin:
            result = detector.process_line(line)
            if result != "NONE":
                print(f"[Phase Detector] → {result}", file=sys.stderr)
                fire_if_needed(result)


if __name__ == "__main__":
    main()
