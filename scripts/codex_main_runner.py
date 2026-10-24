#!/usr/bin/env python3
"""Bounded, single-process continuation controller for the AI Job Agent Main session.

This is intentionally a thin adapter around ``codex exec resume``.  It never
stages, commits, resets, publishes, deploys, or touches the production copy.
"""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import re
import signal
import shlex
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[1]
STATE_DIR = Path(os.environ.get("AI_JOB_AGENT_RUNNER_STATE", "~/.local/state/ai-job-agent/codex-main-runner")).expanduser()
STATE_FILE = STATE_DIR / "state.json"
LOCK_FILE = STATE_DIR / "runner.lock"
LOG_FILE = STATE_DIR / "runner.log"
EVENT_FILE = STATE_DIR / "events.jsonl"
PID_FILE = STATE_DIR / "runner.pid"
DEFAULT_MAX_TURNS = 1
DEFAULT_MAX_NO_PROGRESS = 1


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.chmod(temp, 0o600)
    temp.replace(path)


def read_state() -> dict[str, Any]:
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def event(kind: str, **data: Any) -> None:
    STATE_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
    with EVENT_FILE.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps({"at": now(), "event": kind, **data}, sort_keys=True) + "\n")
    os.chmod(EVENT_FILE, 0o600)


def git(*args: str) -> str:
    result = subprocess.run(["git", *args], cwd=REPO, text=True, capture_output=True, check=False)
    return result.stdout.strip()


def snapshot() -> dict[str, Any]:
    status = git("status", "--short")
    tracked = git("diff", "--binary")
    untracked = git("ls-files", "--others", "--exclude-standard")
    handoff = REPO / "docs/PROJECT_OS/HANDOFF.md"
    roadmap = REPO / "ROADMAP.md"
    material = "\n".join((status, tracked, untracked))
    return {
        "head": git("rev-parse", "HEAD") or "unknown",
        "status": status,
        "dirty_fingerprint": hashlib.sha256(material.encode()).hexdigest(),
        "handoff_mtime_ns": handoff.stat().st_mtime_ns if handoff.exists() else 0,
        "roadmap_mtime_ns": roadmap.stat().st_mtime_ns if roadmap.exists() else 0,
    }


def codex_processes() -> list[str]:
    result = subprocess.run(["ps", "-eo", "pid=,args="], text=True, capture_output=True, check=False)
    found = []
    needle = str(REPO)
    for line in result.stdout.splitlines():
        if needle not in line or str(os.getpid()) in line:
            continue
        try:
            tokens = shlex.split(line)
        except ValueError:
            tokens = line.split()
        # Match the executable itself, not this script's ``codex_main_runner`` path.
        if any(Path(token).name == "codex" for token in tokens[1:]):
            found.append(line.strip())
    return found


def pid_alive(pid: int | None) -> bool:
    if not pid:
        return False
    try:
        os.kill(pid, 0)
    except (ProcessLookupError, PermissionError):
        return False
    return True


def classify(output: str, returncode: int) -> str:
    text = output.lower()
    if re.search(r"rate.?limit|quota|too many requests|429", text):
        return "RATE_LIMIT"
    if re.search(r"authentication|unauthori[sz]ed|login required|invalid api key", text):
        return "AUTH_REQUIRED"
    if re.search(r"blocked|cannot proceed|need (?:your|owner) confirmation|user confirmation", text):
        return "BLOCKED"
    if returncode:
        return "ERROR"
    if "no_progress" in text or "no progress" in text:
        return "NO_PROGRESS"
    if re.search(r"\b(done|complete|completed)\b", text):
        return "DONE"
    return "CONTINUE"


def prompt(turn: int) -> str:
    return f"""You are the continuing Main developer for this repository. This is bounded continuation turn {turn}.
Read docs/PROJECT_OS/BRIEF.md, the current HANDOFF.md, and only relevant ROADMAP.md sections. Choose exactly one useful unfinished task; do not repeat completed fixes or audits. Inspect the dirty worktree first and preserve every existing change. Implement only a small safe dev increment, add meaningful regression tests, run targeted tests plus an appropriate local gate, and update BRIEF.md, DEVELOPMENT_LOG.md, TASKS.md, and HANDOFF.md.
Never run git add, git commit, reset, checkout, push, merge, deploy, production/runtime commands, database/volume changes, or real Telegram/employer messages. Report tests and the exact next task. End with one marker: CONTINUE, DONE, NO_PROGRESS, or BLOCKED (include the reason after the marker)."""


def command(session: str) -> list[str]:
    return ["codex", "--cd", str(REPO), "--sandbox", "workspace-write", "exec", "resume", session, "-"]


class Runner:
    def __init__(self, session: str, max_turns: int, max_no_progress: int) -> None:
        self.session = session
        self.max_turns = max_turns
        self.max_no_progress = max_no_progress
        self.lock_stream = None

    def acquire(self) -> None:
        STATE_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
        self.lock_stream = LOCK_FILE.open("a+")
        try:
            fcntl.flock(self.lock_stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError("runner lock is held; an interactive Main or runner may be active") from exc
        PID_FILE.write_text(str(os.getpid()) + "\n", encoding="utf-8")
        os.chmod(PID_FILE, 0o600)

    def release(self) -> None:
        try:
            PID_FILE.unlink()
        except FileNotFoundError:
            pass
        if self.lock_stream:
            fcntl.flock(self.lock_stream.fileno(), fcntl.LOCK_UN)
            self.lock_stream.close()

    def run(self) -> int:
        self.acquire()
        state = read_state()
        previous = state.get("snapshot")
        no_progress = 0
        try:
            for turn in range(1, self.max_turns + 1):
                if codex_processes():
                    self.finish("BLOCKED", "another Codex process uses this worktree")
                    return 2
                before = snapshot()
                record = {"schema": 1, "status": "RUNNING", "pid": os.getpid(), "session": self.session,
                          "turn": turn, "max_turns": self.max_turns, "snapshot": before, "updated_at": now()}
                write_json(STATE_FILE, record)
                event("turn_started", turn=turn, session=self.session)
                result = subprocess.run(command(self.session), cwd=REPO, input=prompt(turn), text=True,
                                        capture_output=True, check=False)
                output = (result.stdout or "") + ("\n" + result.stderr if result.stderr else "")
                with LOG_FILE.open("a", encoding="utf-8") as log:
                    log.write(f"\n=== turn {turn} {now()} rc={result.returncode} ===\n{output}\n")
                after = snapshot()
                changed = after["head"] != before["head"] or after["dirty_fingerprint"] != before["dirty_fingerprint"] or after["handoff_mtime_ns"] != before["handoff_mtime_ns"] or after["roadmap_mtime_ns"] != before["roadmap_mtime_ns"]
                no_progress = 0 if changed else no_progress + 1
                status = classify(output, result.returncode)
                tests_reported = bool(re.search(r"\b(?:test|tests|pytest|passed|failed)\b", output.lower()))
                next_task_reported = bool(re.search(r"\b(?:next|remaining|continue|done|blocked)\b", output.lower()))
                diff_check = subprocess.run(["git", "diff", "--check"], cwd=REPO, text=True,
                                            capture_output=True, check=False)
                after["tests_reported"] = tests_reported
                after["next_task_reported"] = next_task_reported
                after["diff_check_ok"] = diff_check.returncode == 0
                if status == "CONTINUE" and not tests_reported:
                    status = "BLOCKED"
                    reason = "Codex output did not report a test check"
                elif status == "CONTINUE" and not next_task_reported:
                    status = "BLOCKED"
                    reason = "Codex output did not report the next roadmap/handoff task"
                else:
                    reason = "turn complete"
                if no_progress >= self.max_no_progress and status == "CONTINUE":
                    status = "NO_PROGRESS"
                self.finish(status, reason, turn=turn, snapshot=after, no_progress=no_progress)
                if status != "CONTINUE":
                    return 0 if status in {"DONE", "NO_PROGRESS"} else 2
                previous = after
            self.finish("TURN_LIMIT", "bounded turn limit reached", snapshot=previous or snapshot())
            return 0
        finally:
            self.release()

    def finish(self, status: str, reason: str, **extra: Any) -> None:
        state = {"schema": 1, "status": status, "session": self.session, "reason": reason, "updated_at": now(), **extra}
        write_json(STATE_FILE, state)
        event("runner_state", status=status, reason=reason, **extra)


def doctor(session: str | None) -> int:
    checks: dict[str, Any] = {"repo": str(REPO), "repo_exists": REPO.is_dir(), "git": bool(git("rev-parse", "--show-toplevel")),
                              "codex": bool(subprocess.run(["codex", "--version"], capture_output=True, text=True, check=False).returncode == 0),
                              "session_explicit": bool(session), "active_codex": codex_processes(), "state_dir": str(STATE_DIR)}
    print(json.dumps(checks, indent=2, sort_keys=True))
    return 0 if all((checks["repo_exists"], checks["git"], checks["codex"], checks["session_explicit"])) else 2


def tail() -> int:
    try:
        print(LOG_FILE.read_text(encoding="utf-8")[-12000:])
    except FileNotFoundError:
        print("no runner log yet")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("start", "run", "status", "stop", "logs", "doctor", "dry-run"))
    parser.add_argument("--session", default=os.environ.get("CODEX_MAIN_SESSION_ID"))
    parser.add_argument("--max-turns", type=int, default=DEFAULT_MAX_TURNS)
    parser.add_argument("--max-no-progress", type=int, default=DEFAULT_MAX_NO_PROGRESS)
    args = parser.parse_args()
    if args.action in {"doctor", "dry-run"}:
        return doctor(args.session)
    if args.action == "logs":
        return tail()
    if args.action == "status":
        state = read_state()
        state["pid_alive"] = pid_alive(state.get("pid"))
        state["active_codex"] = codex_processes()
        print(json.dumps(state, indent=2, sort_keys=True))
        return 0
    if args.action == "stop":
        state = read_state()
        pid = state.get("pid")
        if pid_alive(pid):
            os.kill(int(pid), signal.SIGTERM)
            print(f"sent SIGTERM to runner pid {pid}")
        else:
            print("runner is not active")
        return 0
    if not args.session:
        print("refusing to run without --session or CODEX_MAIN_SESSION_ID; never guess --last", file=sys.stderr)
        return 2
    if args.max_turns < 1 or args.max_no_progress < 1:
        print("limits must be positive", file=sys.stderr)
        return 2
    if args.action == "start":
        if codex_processes():
            print("refusing to start while another Codex process references this worktree", file=sys.stderr)
            return 2
        STATE_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
        with LOG_FILE.open("a", encoding="utf-8") as log:
            proc = subprocess.Popen([sys.executable, str(Path(__file__)), "run", "--session", args.session,
                                     "--max-turns", str(args.max_turns), "--max-no-progress", str(args.max_no_progress)],
                                    cwd=REPO, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                                    start_new_session=True)
        print(f"started runner pid {proc.pid}; no Codex turn is started by this command")
        return 0
    return Runner(args.session, args.max_turns, args.max_no_progress).run()


if __name__ == "__main__":
    raise SystemExit(main())
