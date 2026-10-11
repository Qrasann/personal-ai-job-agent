# Local Chat Context

Use the official ChatGPT data export and an explicit title allowlist. The
generated Markdown stays outside this repository and must never be committed.

```bash
python scripts/chat_context.py --list \
  --export "$HOME/Downloads/chatgpt-export/conversations.json"

python scripts/chat_context.py \
  --export "$HOME/Downloads/chatgpt-export/conversations.json" \
  --titles-file "$HOME/codex-private-context/selected-chat-titles.txt" \
  --output-dir "$HOME/codex-private-context/selected-chats"
```

The second command creates `selected_chats.md` with mode `0600`. It exports
only exact, case-insensitive title matches and reports any missing names. Edit
the private titles file to add or remove conversations, then rerun the command.

Codex startup request:

```text
Read AGENTS.md and docs/PROJECT_OS/BRIEF.md. Then read
/home/roma/codex-private-context/selected-chats/selected_chats.md as private
background context. Never copy secrets or sensitive personal facts into Git.
Prefer current repository state over stale statements in old conversations.
```
