from __future__ import annotations

import io
import re

from docx import Document

from app.domain.resume_versions import version_metadata


def _safe_filename(value: str) -> str:
    stem = re.sub(r"[^\w.-]+", "-", value.strip(), flags=re.UNICODE).strip("-.")
    return stem[:80] or "resume"


def export_resume(resume, file_format: str) -> tuple[str, bytes]:
    """Export an explicitly approved stored CV without adding inferred claims."""
    file_format = file_format.casefold()
    if file_format not in {"txt", "docx"}:
        raise ValueError("Формат экспорта: txt или docx.")
    if version_metadata(getattr(resume, "rules", None))["status"] != "approved":
        raise ValueError("Сначала утверди эту версию CV через /resumeapprove.")
    content = str(getattr(resume, "content", "") or "").strip()
    if not content:
        raise ValueError("В этой версии CV нет текста для экспорта.")
    filename = _safe_filename(str(getattr(resume, "name", "") or "resume"))
    if file_format == "txt":
        return f"{filename}.txt", content.encode("utf-8")

    document = Document()
    document.add_heading(str(getattr(resume, "name", "") or "Resume"), level=1)
    metadata = " · ".join(filter(None, (
        str(getattr(resume, "role", "") or "").strip(),
        str(getattr(resume, "language", "") or "").upper().strip(),
    )))
    if metadata:
        document.add_paragraph(metadata)
    for line in content.splitlines():
        document.add_paragraph(line)
    output = io.BytesIO()
    document.save(output)
    return f"{filename}.docx", output.getvalue()
