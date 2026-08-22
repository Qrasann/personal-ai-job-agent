from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def job_keyboard(match_id: int, url: str, can_apply: bool = False, can_prepare: bool = True) -> InlineKeyboardMarkup:
    rows = []
    if can_apply:
        rows.append([
            InlineKeyboardButton(text="✅ Откликнуться", callback_data=f"apply:{match_id}"),
            InlineKeyboardButton(text="❌ Пропустить", callback_data=f"skip:{match_id}"),
        ])
    elif can_prepare:
        rows.append([
            InlineKeyboardButton(text="📝 Подготовить отклик", callback_data=f"prepare:{match_id}"),
            InlineKeyboardButton(text="❌ Пропустить", callback_data=f"skip:{match_id}"),
        ])
    else:
        rows.append([InlineKeyboardButton(text="❌ Пропустить", callback_data=f"skip:{match_id}")])
    if url:
        rows.append([InlineKeyboardButton(text="🔗 Открыть вакансию", url=url)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def recruiter_keyboard(chat_id: str, message_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Отправить ответ", callback_data=f"sendreply:{chat_id}:{message_id}")],
        [InlineKeyboardButton(text="📝 Ответить самому", callback_data=f"manual:{chat_id}:{message_id}"),
         InlineKeyboardButton(text="⏭ Игнорировать", callback_data=f"ignore:{chat_id}:{message_id}")],
    ])
