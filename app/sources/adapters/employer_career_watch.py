from __future__ import annotations

from app.domain.jobs import NormalizedJob, SourceCapabilities
from app.sources.base import JobSource, SourceContext
from app.sources.employer_watchlist import enabled_employers, load_employer_watchlist


class EmployerCareerWatchSource(JobSource):
    """Expose the owner-reviewed official openings to the common match pipeline.

    Provider IDs and links come from the checked-in, validated catalog. The
    catalog's last verification date is retained; unknown location and hiring
    evidence stay unknown instead of being inferred from the market list.
    """

    source_id = "employer_career_watch"
    name = "Employer Career Watch"
    capabilities = SourceCapabilities(discovery=True, details=False, apply=False, messages=False)

    async def discover(self, context: SourceContext) -> list[NormalizedJob]:
        del context  # Curated openings are evaluated independently by each search profile.
        catalog = load_employer_watchlist()
        jobs: list[NormalizedJob] = []
        for employer in enabled_employers():
            for opening in employer.openings:
                jobs.append(NormalizedJob(
                    source=self.source_id,
                    source_job_id=f"{employer.id}:{opening.provider_id}",
                    title=opening.title,
                    company=employer.name,
                    url=opening.url,
                    raw={
                        "provider": employer.ats,
                        "provider_id": opening.provider_id,
                        "employer_id": employer.id,
                        "employer_careers_url": employer.careers_url,
                        "source_location": opening.location,
                        "catalog_verified_at": catalog.verified_at.isoformat(),
                        "curated_suitability": opening.suitability,
                        "work_authorization_evidence": opening.work_authorization,
                        "visa_sponsorship_evidence": opening.visa_sponsorship,
                        "relocation_evidence": opening.relocation,
                    },
                ))
        return jobs
