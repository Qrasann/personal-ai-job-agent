from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def job_keyboard(
    match_id: int,
    url: str,
    can_apply: bool = False,
    can_prepare: bool = True,
    job_id: int | None = None,
) -> InlineKeyboardMarkup:
    rows = []
    if job_id is not None:
        rows.append([InlineKeyboardButton(text="📋 Подробнее", callback_data=f"details:{job_id}")])
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


def jobs_keyboard(rows) -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(
            text=f"📋 #{job.id}",
            callback_data=f"details:{job.id}",
        )
        for match, job in rows
    ]
    return InlineKeyboardMarkup(
        inline_keyboard=[buttons[i:i + 2] for i in range(0, len(buttons), 2)]
    )


def recruiter_keyboard(chat_id: str, message_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Отправить ответ", callback_data=f"sendreply:{chat_id}:{message_id}")],
        [InlineKeyboardButton(text="📝 Ответить самому", callback_data=f"manual:{chat_id}:{message_id}"),
         InlineKeyboardButton(text="⏭ Игнорировать", callback_data=f"ignore:{chat_id}:{message_id}")],
    ])


def vacancy_details_keyboard(job_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🧩 Сравнить с профилем",
                    callback_data=f"compare:{job_id}",
                )
            ]
        ]
    )


def review_keyboard(match_id: int, job_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⭐ Сохранить", callback_data=f"review_save:{match_id}"),
                InlineKeyboardButton(text="❌ Пропустить", callback_data=f"review_skip:{match_id}"),
            ],
            [InlineKeyboardButton(text="📋 Подробнее", callback_data=f"details:{job_id}")],
            [
                InlineKeyboardButton(text="⬅ Назад", callback_data=f"review_prev:{match_id}"),
                InlineKeyboardButton(text="➡ Следующая", callback_data=f"review_next:{match_id}"),
            ],
        ]
    )


def stretch_keyboard(match_id: int, job_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⭐ Сохранить", callback_data=f"stretch_save:{match_id}"),
                InlineKeyboardButton(text="❌ Пропустить", callback_data=f"stretch_skip:{match_id}"),
            ],
            [InlineKeyboardButton(text="📋 Подробнее", callback_data=f"details:{job_id}")],
            [
                InlineKeyboardButton(text="⬅ Назад", callback_data=f"stretch_prev:{match_id}"),
                InlineKeyboardButton(text="➡ Следующая", callback_data=f"stretch_next:{match_id}"),
            ],
        ]
    )


def saved_keyboard(match_id: int, job_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📋 Подробнее", callback_data=f"details:{job_id}")],
            [
                InlineKeyboardButton(text="⬅ Назад", callback_data=f"saved_prev:{match_id}"),
                InlineKeyboardButton(text="➡ Следующая", callback_data=f"saved_next:{match_id}"),
            ],
        ]
    )
