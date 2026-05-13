"""
Convert a Claude Code JSONL transcript into a readable markdown file.

Skips internal noise (thinking blocks, tool results, system reminders,
IDE selection markers) and renders tool_use entries as one-line summaries
so the conversation flow stays visible without drowning in tool dumps.

Usage:
    python3 notes/export_transcript.py [<jsonl path>] [<output md path>]

Defaults assume the most recent transcript for this project under
~/.claude/projects/<encoded-cwd>/.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HOME = Path.home()
DEFAULT_TRANSCRIPT_DIR = (
    HOME / ".claude" / "projects" / "-Users-karenhooper-Desktop-SkypointTest"
)
DEFAULT_OUT = Path(__file__).resolve().parent / "conversation_transcript.md"

# Tags that wrap system-injected user content we don't want in the transcript
NOISE_TAGS = [
    "system-reminder",
    "ide_selection",
    "ide_opened_file",
    "user-prompt-submit-hook",
    "command-message",
    "command-args",
    "local-command-stdout",
    "command-name",
]
NOISE_RE = re.compile(
    r"<(" + "|".join(NOISE_TAGS) + r")>.*?</\1>", re.DOTALL,
)


def latest_transcript() -> Path:
    candidates = sorted(
        DEFAULT_TRANSCRIPT_DIR.glob("*.jsonl"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not candidates:
        sys.exit(f"No .jsonl transcripts found in {DEFAULT_TRANSCRIPT_DIR}")
    return candidates[0]


def strip_noise(text: str) -> str:
    """Drop system-reminder / IDE-context blocks, collapse extra blank lines."""
    text = NOISE_RE.sub("", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text


def render_tool_use(item: dict) -> str:
    name = item.get("name", "?")
    inp = item.get("input", {}) or {}

    if name == "Bash":
        desc = inp.get("description") or ""
        cmd = (inp.get("command") or "").strip().splitlines()[0][:120]
        return f"`Bash` — {desc}: `{cmd}`" if desc else f"`Bash` — `{cmd}`"
    if name in ("Write", "Edit", "Read", "NotebookEdit"):
        path = inp.get("file_path") or ""
        return f"`{name}` — `{path}`"
    if name == "AskUserQuestion":
        qs = inp.get("questions") or []
        if qs:
            return f"`AskUserQuestion` — {qs[0].get('question', '?')}"
        return "`AskUserQuestion`"
    if name == "Skill":
        return f"`Skill` — {inp.get('skill', '?')}"
    if name == "Agent":
        return f"`Agent` — {inp.get('description', '?')}"
    if name == "TodoWrite":
        todos = inp.get("todos") or []
        return f"`TodoWrite` — {len(todos)} item(s)"
    return f"`{name}`"


def extract_text(content) -> str:
    if isinstance(content, str):
        return strip_noise(content)
    if not isinstance(content, list):
        return ""
    parts: list[str] = []
    for item in content:
        if not isinstance(item, dict):
            continue
        t = item.get("type")
        if t == "text":
            txt = strip_noise(item.get("text") or "")
            if txt:
                parts.append(txt)
        elif t == "tool_use":
            parts.append(f"> *(tool call)* {render_tool_use(item)}")
    return "\n\n".join(parts).strip()


def main() -> int:
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else latest_transcript()
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_OUT

    out.parent.mkdir(parents=True, exist_ok=True)

    sections: list[str] = []
    user_turn = 0

    with src.open() as f:
        for line in f:
            rec = json.loads(line)
            if rec.get("type") not in ("user", "assistant"):
                continue
            msg = rec.get("message") or {}
            role = msg.get("role")
            content = msg.get("content")

            text = extract_text(content)
            if not text:
                continue

            # Skip tool_result echoes that came back as role=user
            if role == "user" and isinstance(content, list):
                if all(
                    isinstance(c, dict) and c.get("type") == "tool_result"
                    for c in content
                ):
                    continue

            if role == "user":
                user_turn += 1
                sections.append(f"## Turn {user_turn} — user\n\n{text}\n")
            elif role == "assistant":
                sections.append(f"### assistant\n\n{text}\n")

    header = (
        "# Claude Code conversation transcript\n\n"
        f"Source: `{src}`\n\n"
        "Filtered: tool results, internal thinking, system reminders, and "
        "IDE context tags removed. Tool calls shown as one-line summaries.\n\n"
        "---\n"
    )
    out.write_text(header + "\n".join(sections))

    print(f"Wrote {out} ({out.stat().st_size:,} bytes, {user_turn} user turns)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
