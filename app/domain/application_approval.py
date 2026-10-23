from __future__ import annotations

import hashlib
import json


def application_package_digest(application, channel: str) -> str:
    payload = {
        "application_id": application.id, "job_id": application.job_id,
        "resume_id": application.resume_id, "resume_snapshot": application.resume_snapshot,
        "resume_external_id": application.resume_external_id,
        "vacancy_snapshot": application.vacancy_snapshot or {},
        "message": application.message, "channel": channel,
    }
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()
