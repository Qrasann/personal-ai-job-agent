from urllib.parse import urlparse
import httpx
from app.config import settings


class HHError(RuntimeError):
    pass


class HHAPIForbidden(HHError):
    pass


class HHCaptchaRequired(HHError):
    pass


class HHPrivateAPIUnavailable(HHError):
    pass


class HHClient:
    base_url = "https://api.hh.ru"
    web_base_url = "https://hh.ru"

    def __init__(self) -> None:
        self.headers = {
            "HH-User-Agent": settings.hh_user_agent,
            "User-Agent": settings.hh_user_agent,
            "Accept": "application/json",
        }
        if settings.hh_private_api_enabled and settings.hh_access_token:
            self.headers["Authorization"] = f"Bearer {settings.hh_access_token}"

    @property
    def private_api_available(self) -> bool:
        return bool(settings.hh_private_api_enabled and settings.hh_access_token)

    def _require_private(self) -> None:
        if not self.private_api_available:
            raise HHPrivateAPIUnavailable(
                "Приватные applicant-методы HH отключены. Поиск вакансий работает, "
                "а отклик/чаты выполняются вручную через сайт HH."
            )

    async def _request(self, method: str, url: str, **kwargs) -> httpx.Response:
        if url.startswith("/"):
            url = self.base_url + url
        async with httpx.AsyncClient(timeout=30, follow_redirects=False) as client:
            response = await client.request(method, url, headers=self.headers, **kwargs)
        if response.status_code >= 400:
            try:
                body = response.json()
                body_text = str(body).casefold()
            except Exception:
                body = response.text[:1000]
                body_text = str(body).casefold()
            if "captcha" in body_text:
                raise HHCaptchaRequired(
                    "HH запросил CAPTCHA для API. Агент её не обходит; "
                    "можно продолжить только через обычную публичную страницу HH, если она доступна без проверки."
                )
            if response.status_code == 403:
                raise HHAPIForbidden(f"HH API 403: {body}")
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

    async def search_web(self, text: str, page: int = 0, area: str | None = None) -> str:
        """Read the ordinary public HH search page.

        This is a low-rate discovery fallback only. It never tries to solve or
        bypass CAPTCHA. If HH returns a verification page, discovery stops.
        """
        params = {
            "text": text,
            "search_field": "name",
            "order_by": "publication_time",
            "period": settings.hh_search_period_days,
            "page": page,
        }
        if area:
            params["area"] = area
        headers = {
            "User-Agent": settings.hh_web_user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.7",
        }
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            response = await client.get(f"{self.web_base_url}/search/vacancy", params=params, headers=headers)
        text_body = response.text
        folded = text_body.casefold()
        final_url = str(response.url).casefold()
        if response.status_code >= 400:
            raise HHError(f"HH web {response.status_code}")

        # HH's normal search HTML may contain the literal word ``captcha`` in
        # JavaScript/configuration even when no challenge is being shown.
        # Treat the page as a challenge only when the final URL is a captcha
        # route or explicit human-verification text is visible AND no normal
        # vacancy-search markers are present.
        normal_search_markers = (
            'data-qa="vacancy-serp__vacancy"',
            'data-qa="serp-item__title"',
            "vacancy-serp",
        )
        has_search_content = any(marker in folded for marker in normal_search_markers)
        challenge_markers = (
            "проверка, что вы не робот",
            "подтвердите, что вы человек",
            "подтвердите, что вы не робот",
            "пройдите проверку, чтобы продолжить",
        )
        challenge_url = "/captcha" in final_url or "captcha.hh" in final_url
        explicit_challenge = any(marker in folded for marker in challenge_markers)

        if challenge_url or (explicit_challenge and not has_search_content):
            raise HHCaptchaRequired(
                "Обычная страница HH запросила CAPTCHA/проверку. "
                "Агент остановил HH-поиск; открой сайт вручную."
            )
        return text_body

    async def vacancy(self, vacancy_id: str) -> dict:
        response = await self._request("GET", f"/vacancies/{vacancy_id}")
        return response.json()

    # Everything below this point is private applicant functionality. It is kept
    # for already-authorized legacy accounts, but is not required by the personal MVP.
    async def me(self) -> dict:
        self._require_private()
        response = await self._request("GET", "/me")
        return response.json()

    async def suitable_resumes(self, vacancy_id: str) -> dict:
        self._require_private()
        response = await self._request("GET", f"/vacancies/{vacancy_id}/suitable_resumes")
        return response.json()

    async def apply(self, vacancy_id: str, resume_id: str, message: str = "") -> dict:
        self._require_private()
        data = {"vacancy_id": vacancy_id, "resume_id": resume_id}
        if message:
            data["message"] = message
        files = {k: (None, str(v)) for k, v in data.items()}
        response = await self._request("POST", "/negotiations", files=files)
        location = response.headers.get("Location", "")
        if response.status_code == 303:
            return {"status": "external", "external_url": location, "negotiation_id": None}
        negotiation_id = location.rstrip("/").split("/")[-1] if location else None
        return {"status": "sent", "external_url": None, "negotiation_id": negotiation_id}

    async def active_negotiations(self, only_updates: bool = True) -> dict:
        self._require_private()
        params = {"status": "active", "per_page": 50}
        if only_updates:
            params["has_updates"] = "true"
        response = await self._request("GET", "/negotiations", params=params)
        return response.json()

    async def negotiation_messages(self, negotiation_id: str) -> dict:
        self._require_private()
        response = await self._request("GET", f"/negotiations/{negotiation_id}/messages", params={"per_page": 50})
        return response.json()

    async def send_negotiation_message(self, negotiation_id: str, text: str) -> dict:
        self._require_private()
        response = await self._request("POST", f"/negotiations/{negotiation_id}/messages", data={"message": text})
        try:
            return response.json()
        except Exception:
            return {"ok": True}

    async def chats(self, page: int = 0, per_page: int = 50) -> dict:
        self._require_private()
        response = await self._request("GET", "/common/chats", params={"page": page, "per_page": per_page})
        return response.json()

    async def chat_messages(self, chat_id: str) -> dict:
        self._require_private()
        response = await self._request("GET", f"/common/chats/{chat_id}/messages")
        return response.json()

    async def send_chat_message(self, chat_id: str, text: str) -> dict:
        self._require_private()
        import uuid
        payload = {"idempotency_key": str(uuid.uuid4()), "text": text}
        response = await self._request("POST", f"/common/chats/{chat_id}/messages", json=payload)
        return response.json()
