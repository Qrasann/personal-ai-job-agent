#!/usr/bin/env python3
"""Export an explicit allowlist of ChatGPT conversations to private Markdown."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any


def load_conversations(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("conversations.json must contain a JSON list")
    return [item for item in payload if isinstance(item, dict)]


def load_titles(path: Path) -> list[str]:
    titles: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        title = line.strip()
        if title and not title.startswith("#") and title.casefold() not in {x.casefold() for x in titles}:
            titles.append(title)
    return titles


def active_messages(conversation: dict[str, Any]) -> list[dict[str, Any]]:
    mapping = conversation.get("mapping")
    if not isinstance(mapping, dict):
        return []
    current = conversation.get("current_node")
    nodes: list[dict[str, Any]] = []
    seen: set[str] = set()
    while isinstance(current, str) and current in mapping and current not in seen:
        seen.add(current)
        node = mapping[current]
        if not isinstance(node, dict):
            break
        nodes.append(node)
        current = node.get("parent")
    if not nodes:
        nodes = [node for node in mapping.values() if isinstance(node, dict)]
        nodes.sort(key=lambda node: float((node.get("message") or {}).get("create_time") or 0))
    else:
        nodes.reverse()
    return [node["message"] for node in nodes if isinstance(node.get("message"), dict)]


def message_text(message: dict[str, Any]) -> str:
    content = message.get("content")
    if not isinstance(content, dict):
        return ""
    parts = content.get("parts")
    if not isinstance(parts, list):
        return ""
    text_parts = [part for part in parts if isinstance(part, str) and part.strip()]
    return "\n\n".join(text_parts).strip()


def render_conversation(conversation: dict[str, Any]) -> str:
    title = str(conversation.get("title") or "Без названия").strip()
    lines = [f"# {title}", ""]
    labels = {"user": "User", "assistant": "Assistant", "system": "System"}
    for message in active_messages(conversation):
        author = message.get("author")
        role = str(author.get("role") if isinstance(author, dict) else "").casefold()
        text = message_text(message)
        if role not in labels or not text:
            continue
        lines.extend([f"## {labels[role]}", "", text, ""])
    return "\n".join(lines).rstrip() + "\n"


def export_selected(export_file: Path, titles_file: Path, output_dir: Path) -> tuple[Path, list[str]]:
    conversations = load_conversations(export_file)
    requested = load_titles(titles_file)
    by_title: dict[str, list[dict[str, Any]]] = {}
    for conversation in conversations:
        title = str(conversation.get("title") or "").strip()
        by_title.setdefault(title.casefold(), []).append(conversation)

    selected: list[dict[str, Any]] = []
    missing: list[str] = []
    for title in requested:
        matches = by_title.get(title.casefold(), [])
        if not matches:
            missing.append(title)
            continue
        selected.extend(sorted(matches, key=lambda item: float(item.get("update_time") or 0)))

    output_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(output_dir, 0o700)
    output_file = output_dir / "selected_chats.md"
    header = (
        "# Private selected ChatGPT context\n\n"
        "Generated locally from an explicit title allowlist. Do not commit this file.\n\n"
    )
    body = "\n\n---\n\n".join(render_conversation(item).rstrip() for item in selected)
    output_file.write_text(header + body + ("\n" if body else ""), encoding="utf-8")
    os.chmod(output_file, 0o600)
    return output_file, missing


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--export", type=Path, required=True, help="Path to ChatGPT conversations.json")
    parser.add_argument("--titles-file", type=Path, help="One allowed conversation title per line")
    parser.add_argument("--output-dir", type=Path, help="Private output directory outside the repository")
    parser.add_argument("--list", action="store_true", help="List available conversation titles")
    args = parser.parse_args()

    if args.list:
        titles = sorted({str(item.get("title") or "Без названия") for item in load_conversations(args.export)})
        print("\n".join(titles))
        return 0
    if not args.titles_file or not args.output_dir:
        parser.error("--titles-file and --output-dir are required unless --list is used")

    output_file, missing = export_selected(args.export, args.titles_file, args.output_dir)
    print(f"Exported selected chats to: {output_file}")
    if missing:
        print("Titles not found:")
        for title in missing:
            print(f"- {title}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
