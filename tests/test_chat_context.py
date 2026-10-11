import json

from scripts.chat_context import export_selected


def test_exports_only_allowlisted_active_conversation_branch(tmp_path):
    export_file = tmp_path / "conversations.json"
    titles_file = tmp_path / "titles.txt"
    output_dir = tmp_path / "private"
    export_file.write_text(json.dumps([
        {
            "title": "Keep me",
            "current_node": "a2",
            "mapping": {
                "a1": {"parent": None, "message": {"author": {"role": "user"}, "content": {"parts": ["Question"]}}},
                "a2": {"parent": "a1", "message": {"author": {"role": "assistant"}, "content": {"parts": ["Answer"]}}},
                "branch": {"parent": "a1", "message": {"author": {"role": "assistant"}, "content": {"parts": ["Unused branch"]}}},
            },
        },
        {"title": "Do not export", "mapping": {}},
    ]), encoding="utf-8")
    titles_file.write_text("Keep me\nMissing chat\nKeep me\n", encoding="utf-8")

    output_file, missing = export_selected(export_file, titles_file, output_dir)
    rendered = output_file.read_text(encoding="utf-8")

    assert missing == ["Missing chat"]
    assert "# Keep me" in rendered
    assert "Question" in rendered
    assert "Answer" in rendered
    assert "Unused branch" not in rendered
    assert "Do not export" not in rendered
    assert output_file.stat().st_mode & 0o777 == 0o600
