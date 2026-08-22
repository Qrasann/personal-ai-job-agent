from urllib.parse import urlparse
import httpx
from app.config import settings


class HHError(RuntimeError):
    pass


class HHClient:
    base_url = "https://api.hh.ru"

    def __init__(self) -> None:
        self.headers = {
            "HH-User-Agent": settings.hh_user_agent,
            "User-Agent": settings.hh_user_agent,
            "Accept": "application/json",
        }
        if settings.hh_access_token:
            self.headers["Authorization"] = f"Bearer {settings.hh_access_token}"

    async def _request(self, method: str, url: str, **kwargs) -> httpx.Response:
        if url.startswith("/"):
            url = self.base_url + url
        async with httpx.AsyncClient(timeout=30, follow_redirects=False) as client:
            response = await client.request(method, url, headers=self.headers, **kwargs)
        if response.status_code >= 400:
            try:
                body = response.json()
            except Exception:
                body = response.text[:1000]
            raise HHError(f"HH {response.status_code}: {body}")
        return response

    async def search(self, text: str, page: int = 0, per_page: int = 20, area: str | None = None) -> dict:
        params = {
            "text": text,
            "search_field": "name",
            "order_by": "publication_time",
            "period": settings.hh_search_period_days,
            "page": page,
            "per_page": per_page,
        }
        if area:
            params["area"] = area
        response = await self._request("GET", "/vacancies", params=params)
        return response.json()

    async def vacancy(self, vacancy_id: str) -> dict:
        response = await self._request("GET", f"/vacancies/{vacancy_id}")
        return response.json()

    async def me(self) -> dict:
        response = await self._request("GET", "/me")
        return response.json()

    async def suitable_resumes(self, vacancy_id: str) -> dict:
        response = await self._request("GET", f"/vacancies/{vacancy_id}/suitable_resumes")
        return response.json()

    async def apply(self, vacancy_id: str, resume_id: str, message: str = "") -> dict:
        data = {"vacancy_id": vacancy_id, "resume_id": resume_id}
        if message:
            data["message"] = message
        # HH OpenAPI declares multipart/form-data for POST /negotiations.
        files = {k: (None, str(v)) for k, v in data.items()}
        response = await self._request("POST", "/negotiations", files=files)
        location = response.headers.get("Location", "")
        if response.status_code == 303:
            return {"status": "external", "external_url": location, "negotiation_id": None}
        negotiation_id = location.rstrip("/").split("/")[-1] if location else None
        return {"status": "sent", "external_url": None, "negotiation_id": negotiation_id}

    async def active_negotiations(self, only_updates: bool = True) -> dict:
        params = {"status": "active", "per_page": 50}
        if only_updates:
            params["has_updates"] = "true"
        response = await self._request("GET", "/negotiations", params=params)
        return response.json()

    async def negotiation_messages(self, negotiation_id: str) -> dict:
        response = await self._request("GET", f"/negotiations/{negotiation_id}/messages", params={"per_page": 50})
        return response.json()

    async def send_negotiation_message(self, negotiation_id: str, text: str) -> dict:
        # Current HH endpoint accepts a text message on an existing response/invitation.
        response = await self._request("POST", f"/negotiations/{negotiation_id}/messages", data={"message": text})
        try:
            return response.json()
        except Exception:
            return {"ok": True}

    async def chats(self, page: int = 0, per_page: int = 50) -> dict:
        response = await self._request("GET", "/common/chats", params={"page": page, "per_page": per_page})
        return response.json()

    async def chat_messages(self, chat_id: str) -> dict:
        response = await self._request("GET", f"/common/chats/{chat_id}/messages")
        return response.json()

    async def send_chat_message(self, chat_id: str, text: str) -> dict:
        import uuid
        payload = {"idempotency_key": str(uuid.uuid4()), "text": text}
        response = await self._request("POST", f"/common/chats/{chat_id}/messages", json=payload)
        return response.json()
