from __future__ import annotations

import importlib.util
from pathlib import Path


MODULE = Path(__file__).parents[1] / "scripts" / "codex_main_runner.py"
spec = importlib.util.spec_from_file_location("codex_main_runner", MODULE)
runner = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(runner)


def test_resume_command_is_single_bounded_workspace_turn() -> None:
    command = runner.command("00000000-0000-0000-0000-000000000001")
    assert command[:7] == ["codex", "--cd", str(runner.REPO), "--sandbox", "workspace-write", "exec", "resume"]
    assert command[-2:] == ["00000000-0000-0000-0000-000000000001", "-"]


def test_classification_stops_on_safety_blockers() -> None:
    assert runner.classify("429 rate limit", 1) == "RATE_LIMIT"
    assert runner.classify("authentication required", 1) == "AUTH_REQUIRED"
    assert runner.classify("BLOCKED: need owner confirmation", 0) == "BLOCKED"
    assert runner.classify("finished tests; CONTINUE", 0) == "CONTINUE"


def test_no_progress_fingerprint_is_stable(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(runner, "REPO", tmp_path)
    (tmp_path / "docs/PROJECT_OS").mkdir(parents=True)
    (tmp_path / "docs/PROJECT_OS/HANDOFF.md").write_text("handoff\n", encoding="utf-8")
    (tmp_path / "ROADMAP.md").write_text("roadmap\n", encoding="utf-8")
    monkeypatch.setattr(runner, "git", lambda *args: "same")
    assert runner.snapshot() == runner.snapshot()


def test_do_not_embed_destructive_git_operations() -> None:
    source = MODULE.read_text(encoding="utf-8")
    assert '"add"' not in source
    assert '"commit"' not in source
    assert '"reset"' not in source
    assert '"checkout"' not in source
