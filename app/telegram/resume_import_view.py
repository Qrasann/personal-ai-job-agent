from __future__ import annotations

import html

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.candidates.import_review import plan_fact_import


def render_import_preview(pending: dict, token: str) -> tuple[str, InlineKeyboardMarkup]:
    plan = plan_fact_import(pending["proposals"], pending["overlaps"], pending.get("choices"))
    lines = ["📄 <b>Проверка импорта</b>", "", f"Извлечено символов: {len(pending['content'])}",
             f"Язык: {html.escape(pending['language'])}"]
    if pending["proposals"]:
        lines.extend(["", "Предлагаемые факты:"])
        for proposal in pending["proposals"][:12]:
            lines.append(f"• [{proposal.category}] {html.escape(proposal.value[:180])} — уверенность {proposal.confidence:.0%}")
        if len(pending["proposals"]) > 12:
            lines.append(f"… и ещё {len(pending['proposals']) - 12}")
    else:
        lines.extend(["", "Новых фактов для добавления не найдено."])
    if pending.get("duplicates_count"):
        lines.append(f"Совпадающих фактов пропущено: {pending['duplicates_count']}.")
    if pending["overlaps"]:
        lines.extend(["", "Пересечения по умолчанию: KEEP — оставить текущий факт.",
                      "ADD — отдельный факт. UPDATE — заменить активный факт; старый останется в истории.",
                      "Новые и заменённые факты имеют тип unknown; коммерческий опыт не подтверждается импортом."])
    lines.extend(["", f"ADD: {len(plan.additions)} · UPDATE: {len(plan.replacements)} · KEEP: {plan.kept}",
                  "Содержимое будет сохранено только после подтверждения."])
    rows = [
        [InlineKeyboardButton(text="Сохранить резюме", callback_data=f"rimp:resume:{token}")],
        [InlineKeyboardButton(text=f"Сохранить резюме и выбранные факты ({len(plan.additions) + len(plan.replacements)})", callback_data=f"rimp:facts:{token}")],
    ]
    if pending["overlaps"]:
        rows.append([InlineKeyboardButton(text=f"Разобрать пересечения ({len(pending['overlaps'])})", callback_data=f"rimp:review:{token}")])
    rows.append([InlineKeyboardButton(text="Отмена", callback_data=f"rimp:cancel:{token}")])
    return "\n".join(lines)[:4096], InlineKeyboardMarkup(inline_keyboard=rows)


def render_import_conflict(pending: dict, token: str, index: int | None = None) -> tuple[str, InlineKeyboardMarkup]:
    indexed = {pending["proposals"].index(overlap.proposal): overlap for overlap in pending["overlaps"]}
    indices = sorted(indexed)
    index = indices[0] if index is None and indices else index
    if index not in indexed:
        raise ValueError("Пересечение не найдено.")
    overlap = indexed[index]
    position = indices.index(index)
    action = pending.get("choices", {}).get(index, "keep")
    text = (f"🧠 <b>Пересечение {position + 1}/{len(indices)}</b>\n\n"
            f"Текущий факт #{overlap.existing_id}:\n{html.escape(overlap.existing_value[:300])}\n\n"
            f"Из резюме:\n{html.escape(overlap.proposal.value[:300])}\n\n"
            f"Выбор: <b>{action.upper()}</b>\n"
            "ADD — добавить отдельно; KEEP — сохранить текущий факт.\n"
            "UPDATE — старый факт останется в истории, новый получит тип unknown.\n"
            "Выбор применится только после сохранения резюме и выбранных фактов.")
    rows = [[InlineKeyboardButton(text=("✓ " if action == choice else "") + choice.upper(),
                                  callback_data=f"rchoice:{token}:{index}:{choice}")
             for choice in ("add", "update", "keep")]]
    navigation = []
    if position:
        navigation.append(InlineKeyboardButton(text="←", callback_data=f"rchoice:{token}:{indices[position - 1]}:show"))
    if position + 1 < len(indices):
        navigation.append(InlineKeyboardButton(text="→", callback_data=f"rchoice:{token}:{indices[position + 1]}:show"))
    if navigation:
        rows.append(navigation)
    rows.append([InlineKeyboardButton(text="Вернуться к подтверждению", callback_data=f"rchoice:{token}:0:summary")])
    return text, InlineKeyboardMarkup(inline_keyboard=rows)
