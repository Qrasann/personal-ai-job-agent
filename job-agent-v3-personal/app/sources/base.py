from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.domain.jobs import NormalizedJob, SourceCapabilities


@dataclass(slots=True)
class SourceContext:
    user_id: int
    current_country: str | None = None
    target_countries: list[str] | None = None
    queries: list[str] | None = None


class JobSource(ABC):
    source_id: str
    name: str
    capabilities = SourceCapabilities()

    @abstractmethod
    async def discover(self, context: SourceContext) -> list[NormalizedJob]:
        raise NotImplementedError

    async def apply(self, *args, **kwargs):
        raise NotImplementedError(f"{self.source_id} does not support automated apply")

    async def get_messages(self, *args, **kwargs):
        raise NotImplementedError(f"{self.source_id} does not support messages")

    async def send_message(self, *args, **kwargs):
        raise NotImplementedError(f"{self.source_id} does not support messages")
