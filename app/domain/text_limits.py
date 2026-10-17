"""Length accounting for bounded Telegram text and entity offsets."""


def utf16_length(text: str) -> int:
    return len(text.encode("utf-16-le")) // 2
