import asyncio
import ssl
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock

import httpx

from app import services
from app.domain.jobs import NormalizedJob


def configure_scan(monkeypatch, sources, priorities=None):
    async def context(user_id):
        return (
            SimpleNamespace(id=7, current_country="RU", telegram_chat_id="123"),
            SimpleNamespace(target_role="DevOps"),
            [SimpleNamespace(id=11, name="Career-first", settings={
                "queries": ["DevOps"],
                "source_priorities": priorities or {},
            })],
        )

    monkeypatch.setattr(services, "_user_context", context)
    monkeypatch.setattr(services, "_DISCOVERY_CACHE", {})
    monkeypatch.setattr(services, "_HH_CONNECT_RETRY_AFTER", 0.0)
    monkeypatch.setattr(services, "_HH_DISCOVERY_LOCK", asyncio.Lock())
    monkeypatch.setattr(services.repo, "get_state", AsyncMock(return_value="false"))
    monkeypatch.setattr(services, "build_source_plan", lambda *a, **k: [
        SimpleNamespace(source_id=name, implemented=True) for name in sources
    ])
    for name, factory in sources.items():
        adapter = {"hh": "HHSource", "remoteok": "RemoteOKSource", "arbeitnow": "ArbeitnowSource", "smartrecruiters": "SmartRecruitersSource", "eures": "EuresSource"}[name]
        monkeypatch.setattr(services, adapter, factory)


def test_scheduled_scan_continues_after_one_user_fails(monkeypatch, caplog):
    users = [SimpleNamespace(id=1), SimpleNamespace(id=2)]
    seen = []

    monkeypatch.setattr(services.repo, "list_active_users", AsyncMock(return_value=users))

    monkeypatch.setattr(services.repo, "set_state", AsyncMock())

    async def scan(bot, user_id):
        seen.append(user_id)
        if user_id == 1:
            raise RuntimeError("temporary database failure")
        return {"sources": {}}

    monkeypatch.setattr(services, "scan_for_user", scan)
    asyncio.run(services.scan_all(object()))

    assert seen == [1, 2]
    assert "scheduled scan failed for user 1" in caplog.text


def test_raw_tls_failure_is_safe_in_logs_summary_and_alert(monkeypatch, caplog):
    class Eures:
        source_id = name = "eures"

        async def discover(self, context):
            raise ssl.SSLError("https://feed.test/?token=private-value")

    configure_scan(monkeypatch, {"eures": Eures})
    alerts = AsyncMock()
    monkeypatch.setattr(services, "notify_chat", alerts)

    summary = asyncio.run(services.scan_for_user(object(), 7))

    assert summary["sources"]["eures"]["error"] == "TLS_CONNECTION_FAILED"
    assert "category=tls" in caplog.text
    assert "private-value" not in caplog.text
    assert "private-value" not in alerts.await_args.args[2]


def test_source_timeout_and_error_do_not_discard_successful_discovery(monkeypatch):
    cancelled = []
    matched = []

    class Source:
        def __init__(self, name, *args):
            self.source_id = self.name = name

        async def discover(self, context):
            if self.source_id == "remoteok":
                raise RuntimeError("remote feed unavailable")
            if self.source_id == "arbeitnow":
                try:
                    await asyncio.sleep(1)
                except asyncio.CancelledError:
                    cancelled.append(self.source_id)
                    raise
            return [NormalizedJob(source="hh", source_job_id="1", title="DevOps")]

    async def ingest(bot, job, **kwargs):
        matched.append((job.source, kwargs["only_search_profile_id"]))
        return {"processed": 1}

    configure_scan(monkeypatch, {
        "hh": lambda *a: Source("hh"),
        "remoteok": lambda: Source("remoteok"),
        "arbeitnow": lambda: Source("arbeitnow"),
    })
    monkeypatch.setattr(services, "DISCOVERY_TIMEOUT_SECONDS", 0.02)
    monkeypatch.setattr(services, "ingest_and_match", ingest)
    alerts = AsyncMock()
    monkeypatch.setattr(services, "notify_chat", alerts)

    summary = asyncio.run(services.scan_for_user(object(), 7, force_refresh=True))

    assert matched == [("hh", 11)]
    assert cancelled == ["arbeitnow"]
    assert summary["processed"] == 1
    assert summary["sources"]["hh"]["found"] == 1
    assert summary["sources"]["remoteok"]["error"] == "SOURCE_PROCESSING_FAILED"
    assert summary["sources"]["arbeitnow"]["error"] == "SOURCE_DISCOVERY_TIMEOUT"
    assert all("duration_ms" in info for info in summary["sources"].values())
    assert alerts.await_count == 2
    assert set(summary["searches"]["11"]["sources"]) == {"hh", "remoteok", "arbeitnow"}


def test_one_bad_vacancy_does_not_discard_later_results_from_source(monkeypatch):
    class Source:
        source_id = name = "remoteok"

        async def discover(self, _context):
            return [
                NormalizedJob(source="remoteok", source_job_id="bad", title="DevOps"),
                NormalizedJob(source="remoteok", source_job_id="good", title="DevOps"),
            ]

    async def ingest(_bot, job, **_kwargs):
        if job.source_job_id == "bad":
            raise ValueError("malformed vacancy")
        return {"processed": 1}

    configure_scan(monkeypatch, {"remoteok": Source})
    monkeypatch.setattr(services, "ingest_and_match", ingest)
    monkeypatch.setattr(services, "notify_chat", AsyncMock())

    summary = asyncio.run(services.scan_for_user(object(), 7, force_refresh=True))

    assert summary["processed"] == 1
    assert summary["sources"]["remoteok"]["found"] == 2
    assert summary["sources"]["remoteok"]["partial"] is True
    assert summary["searches"]["11"]["sources"]["remoteok"]["processing_errors"] == 1


def test_scan_summary_counts_nonempty_source_publication_date_fields(monkeypatch):
    class Source:
        source_id = name = "remoteok"

        async def discover(self, _context):
            return [
                NormalizedJob(source="remoteok", source_job_id="dated", title="DevOps", published_at="2026-10-01"),
                NormalizedJob(source="remoteok", source_job_id="undated", title="DevOps", published_at="  "),
                NormalizedJob(source="remoteok", source_job_id="unknown", title="DevOps"),
            ]

    configure_scan(monkeypatch, {"remoteok": Source})
    monkeypatch.setattr(services, "ingest_and_match", AsyncMock(return_value={"processed": 1}))
    monkeypatch.setattr(services, "notify_chat", AsyncMock())

    summary = asyncio.run(services.scan_for_user(object(), 7, force_refresh=True))
    info = summary["sources"]["remoteok"]
    assert info["found"] == 3
    assert info["publication_date_provided"] == 1
    assert info["publication_date_missing"] == 2


def test_scan_summary_counts_publication_age_without_filtering_or_guessing_timezone(monkeypatch):
    now = datetime.now(UTC)

    class Source:
        source_id = name = "remoteok"

        async def discover(self, _context):
            return [
                NormalizedJob(source="remoteok", source_job_id="fresh", title="DevOps", published_at=(now - timedelta(days=2)).isoformat()),
                NormalizedJob(source="remoteok", source_job_id="middle", title="DevOps", published_at=(now - timedelta(days=14)).isoformat()),
                NormalizedJob(source="remoteok", source_job_id="old", title="DevOps", published_at=(now - timedelta(days=45)).isoformat()),
                NormalizedJob(source="remoteok", source_job_id="naive", title="DevOps", published_at=(now.replace(tzinfo=None)).isoformat()),
                NormalizedJob(source="remoteok", source_job_id="missing", title="DevOps"),
            ]

    configure_scan(monkeypatch, {"remoteok": Source})
    monkeypatch.setattr(services, "ingest_and_match", AsyncMock(return_value={"processed": 1}))
    monkeypatch.setattr(services, "notify_chat", AsyncMock())

    summary = asyncio.run(services.scan_for_user(object(), 7, force_refresh=True))
    info = summary["sources"]["remoteok"]

    assert info["found"] == 5
    assert info["publication_age_0_7d"] == 1
    assert info["publication_age_8_30d"] == 1
    assert info["publication_age_over_30d"] == 1
    assert info["publication_age_unknown"] == 2


def test_scan_summary_keeps_scoring_filter_reasons_from_ingestion(monkeypatch):
    class Source:
        source_id = name = "remoteok"

        async def discover(self, _context):
            return [NormalizedJob(source="remoteok", source_job_id="hard", title="DevOps")]

    configure_scan(monkeypatch, {"remoteok": Source})
    monkeypatch.setattr(services, "ingest_and_match", AsyncMock(return_value={
        "processed": 1, "filtered": 1,
        "scoring_exclusion_reasons": {"technical_gap": 1},
    }))
    monkeypatch.setattr(services, "notify_chat", AsyncMock())

    summary = asyncio.run(services.scan_for_user(object(), 7, force_refresh=True))

    assert summary["sources"]["remoteok"]["scoring_exclusion_reasons"] == {
        "technical_gap": 1,
    }
    assert summary["searches"]["11"]["scoring_exclusion_reasons"] == {
        "technical_gap": 1,
    }


def test_source_summary_explains_zero_relocation_yield_without_losing_career_results(monkeypatch):
    class Source:
        source_id = name = "remoteok"

        async def discover(self, _context):
            return [NormalizedJob(
                source="remoteok", source_job_id="domestic", title="DevOps",
                country="RU", work_mode="onsite",
            )]

    configure_scan(monkeypatch, {"remoteok": Source})
    original_context = services._user_context

    async def two_profiles(user_id):
        user, profile, searches = await original_context(user_id)
        searches.append(SimpleNamespace(id=12, name="Relocation-first", settings={
            "queries": ["DevOps"], "search_strategy": "relocation_first",
        }))
        return user, profile, searches

    monkeypatch.setattr(services, "_user_context", two_profiles)
    ingest = AsyncMock(return_value={"processed": 1})
    monkeypatch.setattr(services, "ingest_and_match", ingest)
    monkeypatch.setattr(services, "notify_chat", AsyncMock())
    summary = asyncio.run(services.scan_for_user(object(), 7))

    career = summary["searches"]["11"]["sources"]["remoteok"]
    relocation = summary["searches"]["12"]["sources"]["remoteok"]
    assert (career["discovered"], career["found"], career["preference_filtered"]) == (1, 1, 0)
    assert (relocation["discovered"], relocation["found"], relocation["preference_filtered"]) == (1, 0, 1)
    assert relocation["preference_exclusion_reasons"] == {"domestic_onsite": 1}
    assert summary["searches"]["12"]["preference_exclusion_reasons"] == {
        "domestic_onsite": 1,
    }
    assert relocation["status"] == "success"
    assert summary["sources"]["remoteok"]["discovered"] == 2
    assert summary["sources"]["remoteok"]["preference_filtered"] == 1
    assert summary["sources"]["remoteok"]["preference_exclusion_reasons"] == {"domestic_onsite": 1}
    ingest.assert_awaited_once()
    assert ingest.await_args.kwargs["only_search_profile_id"] == 11


def test_partial_source_failures_are_preserved_in_scan_summary(monkeypatch):
    class Eures:
        source_id = name = "eures"

        def __init__(self, *args):
            self.partial_failures = 0

        async def discover(self, context):
            self.partial_failures = 2
            return [NormalizedJob(source="eures", source_job_id="partial-1", title="DevOps Engineer")]

    configure_scan(monkeypatch, {"eures": Eures})
    monkeypatch.setattr(services, "ingest_and_match", AsyncMock(return_value={"processed": 1}))
    monkeypatch.setattr(services, "notify_chat", AsyncMock())

    original_context = services._user_context

    async def two_profiles(user_id):
        user, profile, searches = await original_context(user_id)
        searches.append(SimpleNamespace(id=12, name="Relocation-first", settings={"queries": ["DevOps"]}))
        return user, profile, searches

    monkeypatch.setattr(services, "_user_context", two_profiles)

    summary = asyncio.run(services.scan_for_user(object(), 7))

    assert summary["sources"]["eures"]["partial"] is True
    assert summary["sources"]["eures"]["partial_failures"] == 2
    assert summary["searches"]["11"]["sources"]["eures"]["partial_failures"] == 2
    assert summary["searches"]["12"]["sources"]["eures"]["partial_failures"] == 2


def test_later_profile_success_preserves_source_processing_errors(monkeypatch):
    class Source:
        source_id = name = "remoteok"

        async def discover(self, context):
            return [NormalizedJob(source="remoteok", source_job_id="same", title="DevOps")]

    configure_scan(monkeypatch, {"remoteok": Source})
    original_context = services._user_context

    async def two_profiles(user_id):
        user, profile, searches = await original_context(user_id)
        searches.append(SimpleNamespace(id=12, name="Relocation-first", settings={"queries": ["DevOps"]}))
        return user, profile, searches

    async def ingest(bot, job, *, only_user_id, only_search_profile_id):
        if only_search_profile_id == 11:
            raise ValueError("profile-specific malformed result")
        return {"processed": 1}

    monkeypatch.setattr(services, "_user_context", two_profiles)
    monkeypatch.setattr(services, "ingest_and_match", ingest)

    summary = asyncio.run(services.scan_for_user(object(), 7))

    assert summary["processed"] == 1
    assert summary["sources"]["remoteok"]["partial"] is True
    assert summary["sources"]["remoteok"]["processing_errors"] == 1
    assert summary["searches"]["11"]["sources"]["remoteok"]["processing_errors"] == 1


def test_distinct_cached_discoveries_keep_all_partial_failure_counts(monkeypatch):
    class Eures:
        source_id = name = "eures"

        async def discover(self, context):
            self.partial_failures = 2 if context.queries == ["DevOps"] else 3
            return []

    configure_scan(monkeypatch, {"eures": Eures})
    original_context = services._user_context

    async def two_profiles(user_id):
        user, profile, searches = await original_context(user_id)
        searches.append(SimpleNamespace(id=12, name="Relocation-first", settings={"queries": ["Cloud"]}))
        return user, profile, searches

    monkeypatch.setattr(services, "_user_context", two_profiles)

    async def scenario():
        live = await services.scan_for_user(object(), 7)
        cached = await services.scan_for_user(object(), 7)
        return live, cached

    live, cached = asyncio.run(scenario())

    assert live["sources"]["eures"]["partial_failures"] == 5
    assert cached["sources"]["eures"]["cache"] is True
    assert cached["sources"]["eures"]["partial_failures"] == 5


def test_ingestion_respects_source_priority_when_discovery_finishes_out_of_order(monkeypatch):
    discovered = []
    matched = []

    class Source:
        def __init__(self, name, delay):
            self.source_id = self.name = name
            self.delay = delay

        async def discover(self, context):
            await asyncio.sleep(self.delay)
            discovered.append(self.source_id)
            return [NormalizedJob(source=self.source_id, source_job_id="1", title="DevOps")]

    async def ingest(bot, job, **kwargs):
        matched.append(job.source)
        return {"processed": 1}

    configure_scan(monkeypatch, {
        "hh": lambda *a: Source("hh", 0),
        "remoteok": lambda: Source("remoteok", 0.02),
        "arbeitnow": lambda: Source("arbeitnow", 0.01),
    }, {"hh": 25, "remoteok": 100, "arbeitnow": 50})
    monkeypatch.setattr(services, "ingest_and_match", ingest)

    summary = asyncio.run(services.scan_for_user(object(), 7, force_refresh=True))

    assert discovered == ["hh", "arbeitnow", "remoteok"]
    assert matched == ["remoteok", "arbeitnow", "hh"]
    assert summary["processed"] == 3


def test_hh_connect_error_is_silent_and_rechecked_after_cooldown(monkeypatch):
    calls = []
    alerts = AsyncMock()

    class Source:
        def __init__(self, name, *args):
            self.source_id = self.name = name

        async def discover(self, context):
            calls.append(self.source_id)
            if self.source_id == "hh":
                raise httpx.ConnectError("temporary connection failure")
            return []

    configure_scan(monkeypatch, {
        "hh": lambda *a: Source("hh"),
        "remoteok": lambda: Source("remoteok"),
    })
    monkeypatch.setattr(services, "_HH_CONNECT_RETRY_AFTER", 0.0)
    monkeypatch.setattr(services, "notify_chat", alerts)
    monkeypatch.setattr(services, "HH_CONNECT_RECHECK_SECONDS", 0.05)

    original_context = services._user_context

    async def two_profiles(user_id):
        user, profile, searches = await original_context(user_id)
        searches.append(SimpleNamespace(id=12, name="Relocation-first", settings={"queries": ["DevOps"]}))
        return user, profile, searches

    monkeypatch.setattr(services, "_user_context", two_profiles)
    summary = asyncio.run(services.scan_for_user(object(), 7, force_refresh=True))

    assert calls.count("hh") == 1
    assert calls.count("remoteok") == 2
    assert alerts.await_count == 0
    assert summary["sources"]["hh"]["failed"] == 1
    assert summary["sources"]["hh"]["skipped"] == 1
    assert summary["searches"]["12"]["sources"]["hh"]["status"] == "skipped"

    calls.clear()
    asyncio.run(asyncio.sleep(0.06))
    asyncio.run(services.scan_for_user(object(), 7, force_refresh=True))
    assert calls.count("hh") == 1


def test_hh_connect_timeout_is_rechecked_after_cooldown_and_keeps_safe_notice(monkeypatch):
    calls = []
    alerts = AsyncMock()

    class Source:
        source_id = name = "hh"

        async def discover(self, context):
            calls.append(context.user_id)
            raise httpx.ConnectTimeout("https://private.test/?token=secret")

    configure_scan(monkeypatch, {"hh": lambda *args: Source()})
    monkeypatch.setattr(services, "_HH_CONNECT_RETRY_AFTER", 0.0)
    monkeypatch.setattr(services, "HH_CONNECT_RECHECK_SECONDS", 900)
    original_context = services._user_context

    async def two_profiles(user_id):
        user, profile, searches = await original_context(user_id)
        searches.append(SimpleNamespace(id=12, name="Relocation-first", settings={"queries": ["DevOps"]}))
        return user, profile, searches

    monkeypatch.setattr(services, "_user_context", two_profiles)
    monkeypatch.setattr(services, "notify_chat", alerts)
    summary = asyncio.run(services.scan_for_user(object(), 7, force_refresh=True))

    assert calls == [7]
    assert summary["sources"]["hh"]["failed"] == 1
    assert summary["sources"]["hh"]["skipped"] == 1
    assert alerts.await_count == 1
    notice = alerts.await_args.args[2]
    assert "NETWORK_CONNECT_TIMEOUT" in notice
    assert "Причина устанавливается" in notice
    assert "secret" not in notice
    assert services._HH_CONNECT_RETRY_AFTER > 0


def test_hh_failure_invalidates_old_cache_so_next_scheduled_scan_probes(monkeypatch):
    calls = []

    class HH:
        source_id = name = "hh"

        async def discover(self, context):
            calls.append("hh")
            if len(calls) == 2:
                raise httpx.ConnectError("offline")
            return []

    configure_scan(monkeypatch, {"hh": lambda *a: HH()})
    alerts = AsyncMock()
    monkeypatch.setattr(services, "notify_chat", alerts)
    asyncio.run(services.scan_for_user(object(), 7))
    assert any(key[0] == "hh" for key in services._DISCOVERY_CACHE)

    asyncio.run(services.scan_for_user(object(), 7, force_refresh=True))
    assert not any(key[0] == "hh" for key in services._DISCOVERY_CACHE)
    monkeypatch.setattr(services, "_HH_CONNECT_RETRY_AFTER", 0.0)
    summary = asyncio.run(services.scan_for_user(object(), 7))
    assert calls == ["hh", "hh", "hh"]
    assert summary["sources"]["hh"]["cache"] is False
    alerts.assert_not_awaited()


def test_smartrecruiters_wiring_caches_discovery_and_respects_disabled_source(monkeypatch):
    calls = []

    class Source:
        source_id = name = "smartrecruiters"

        async def discover(self, context):
            calls.append(context.user_id)
            return [NormalizedJob(source=self.source_id, source_job_id="Devexperts:1", title="DevOps", country="GE")]

    configure_scan(monkeypatch, {"smartrecruiters": Source})
    monkeypatch.setattr(services, "ingest_and_match", AsyncMock(return_value={"processed": 1}))
    first = asyncio.run(services.scan_for_user(object(), 7))
    second = asyncio.run(services.scan_for_user(object(), 7))
    assert first["sources"]["smartrecruiters"]["found"] == 1
    assert second["sources"]["smartrecruiters"]["cache"] is True
    assert len(calls) == 1
    assert services._cache_ttl("smartrecruiters") == 6 * 60 * 60

    original_context = services._user_context

    async def disabled_context(user_id):
        user, profile, searches = await original_context(user_id)
        searches[0].settings["disabled_sources"] = ["smartrecruiters"]
        return user, profile, searches

    monkeypatch.setattr(services, "_user_context", disabled_context)
    disabled = asyncio.run(services.scan_for_user(object(), 7, force_refresh=True))
    assert "smartrecruiters" not in disabled["sources"]
    assert len(calls) == 1


def test_concurrent_hh_failure_uses_one_probe_and_keeps_other_sources(monkeypatch):
    calls = []

    class Source:
        def __init__(self, name):
            self.source_id = self.name = name

        async def discover(self, context):
            calls.append(self.source_id)
            if self.source_id == "hh":
                await asyncio.sleep(0)
                raise httpx.ConnectError("offline")
            return []

    configure_scan(monkeypatch, {
        "hh": lambda *a: Source("hh"),
        "remoteok": lambda: Source("remoteok"),
    })
    alerts = AsyncMock()
    monkeypatch.setattr(services, "notify_chat", alerts)

    async def concurrent_scans():
        return await asyncio.gather(
            services.scan_for_user(object(), 7, force_refresh=True),
            services.scan_for_user(object(), 7, force_refresh=True),
        )

    summaries = asyncio.run(concurrent_scans())
    assert calls.count("hh") == 1
    assert calls.count("remoteok") == 2
    assert all("skipped" in result["sources"]["hh"] for result in summaries)
    assert all(result["sources"]["remoteok"]["found"] == 0 for result in summaries)
    alerts.assert_not_awaited()


def test_hh_recovery_between_profiles_retains_count_and_marks_partial(monkeypatch):
    calls = []

    class HH:
        source_id = name = "hh"

        async def discover(self, context):
            calls.append("hh")
            if len(calls) == 1:
                raise httpx.ConnectError("offline")
            return [NormalizedJob(source="hh", source_job_id="1", title="DevOps")]

    configure_scan(monkeypatch, {"hh": lambda *a: HH()})
    original_context = services._user_context

    async def two_profiles(user_id):
        user, profile, searches = await original_context(user_id)
        searches.append(SimpleNamespace(id=12, name="Relocation-first", settings={"queries": ["DevOps"]}))
        return user, profile, searches

    async def progress(text):
        # Simulate a long scan where the cooldown expires before profile 2.
        if "Relocation-first" in text:
            monkeypatch.setattr(services, "_HH_CONNECT_RETRY_AFTER", 0.0)

    monkeypatch.setattr(services, "_user_context", two_profiles)
    monkeypatch.setattr(services, "ingest_and_match", AsyncMock(return_value={"processed": 1}))
    alerts = AsyncMock()
    monkeypatch.setattr(services, "notify_chat", alerts)
    summary = asyncio.run(services.scan_for_user(object(), 7, progress, force_refresh=True))

    assert summary["sources"]["hh"]["found"] == 1
    assert summary["sources"]["hh"]["partial"] is True
    assert summary["sources"]["hh"]["skipped"] == 0
    assert summary["sources"]["hh"]["failed"] == 1
    assert summary["searches"]["11"]["sources"]["hh"]["status"] == "failed"
    assert summary["searches"]["12"]["sources"]["hh"]["found"] == 1
    assert summary["processed"] == 1
    alerts.assert_not_awaited()


def test_two_profile_timeouts_have_one_safe_alert_and_two_observations(monkeypatch):
    class Remote:
        source_id = 'remoteok'
        name = 'Remote OK'
        async def discover(self, context):
            raise httpx.ConnectTimeout('https://private.test/?token=secret')
    configure_scan(monkeypatch, {'remoteok':Remote})
    original = services._user_context
    async def context(user_id):
        user, profile, searches = await original(user_id)
        searches.append(SimpleNamespace(id=12, name='Relocation-first', settings={'queries':['DevOps']}))
        return user, profile, searches
    monkeypatch.setattr(services,'_user_context',context)
    alerts = AsyncMock()
    monkeypatch.setattr(services,'notify_chat',alerts)
    summary=asyncio.run(services.scan_for_user(object(),7,force_refresh=True))
    info=summary['sources']['remoteok']
    assert info['failed']==2
    assert info['found']==0
    assert len(info['history'])==2
    assert len(info['diagnostics'])==2
    assert alerts.await_count==1
    text=alerts.await_args.args[2]
    assert 'Career-first / Relocation-first' in text
    assert 'NETWORK_CONNECT_TIMEOUT' in text
    assert 'secret' not in text
    assert '&#' not in text
    assert alerts.await_args.kwargs['parse_mode'] is None


def test_prefilter_failure_keeps_other_jobs_and_classifies_processing(monkeypatch):
    class Remote:
        source_id=name='remoteok'
        async def discover(self, context):
            return [NormalizedJob(source='remoteok',source_job_id=str(n),title='DevOps') for n in (1,2)]
    configure_scan(monkeypatch,{'remoteok':Remote})
    def allowed(job,*args,**kwargs):
        if job.source_job_id=='1':
            raise KeyError('private field')
        return True
    monkeypatch.setattr(services,'vacancy_allowed',allowed)
    ingest=AsyncMock(return_value={'processed':1,'qualified':1})
    monkeypatch.setattr(services,'ingest_and_match',ingest)
    monkeypatch.setattr(services,'notify_chat',AsyncMock())
    summary=asyncio.run(services.scan_for_user(object(),7))
    info=summary['sources']['remoteok']
    assert summary['processed']==1
    assert info['status']=='partial'
    assert info['processing_errors']==1
    assert info['discovered'] == 2
    assert info['preference_filtered'] == 0
    assert info['processed']==info['qualified']==1
    assert info['diagnostics'][0]['stage']=='processing'
    assert 'private field' not in str(summary)


def test_summary_failure_does_not_become_provider_failure(monkeypatch):
    class Remote:
        source_id=name='remoteok'
        async def discover(self, context):
            return [NormalizedJob(source='remoteok',source_job_id='1',title='DevOps')]
    configure_scan(monkeypatch,{'remoteok':Remote})
    monkeypatch.setattr(services,'ingest_and_match',AsyncMock(return_value={'processed':1}))
    monkeypatch.setattr(services,'_aggregate_source',lambda *args: (_ for _ in ()).throw(KeyError('found')))
    alerts=AsyncMock()
    monkeypatch.setattr(services,'notify_chat',alerts)
    summary=asyncio.run(services.scan_for_user(object(),7))
    info=summary['sources']['remoteok']
    assert info['found']==info['processed']==1
    assert info['status']=='partial'
    assert info['failed']==0
    assert info['diagnostics'][0]['code']=='SOURCE_SUMMARY_MISSING_FIELD'
    assert 'статистика приложения' in alerts.await_args.args[2]


def test_scheduled_summary_persists_partial_history_per_user(monkeypatch):
    import json
    monkeypatch.setattr(services.repo,'list_active_users',AsyncMock(return_value=[SimpleNamespace(id=7)]))
    summary={'sources':{'remoteok':{'found':2,'partial':True,'diagnostics':[]}}}
    monkeypatch.setattr(services,'scan_for_user',AsyncMock(return_value=summary))
    save=AsyncMock()
    monkeypatch.setattr(services.repo,'set_state',save)
    asyncio.run(services.scan_all(object()))
    assert save.await_args.args[:2]==(7,'scheduled_scan_dashboard')
    state=json.loads(save.await_args.args[2])
    assert state['status']=='partial'
    assert state['kind']=='scheduled'
    assert state['summary']==summary
    assert state['started_at']<=state['finished_at']


def test_scheduled_history_write_failure_does_not_stop_next_user(monkeypatch,caplog):
    monkeypatch.setattr(services.repo,'list_active_users',AsyncMock(return_value=[SimpleNamespace(id=1),SimpleNamespace(id=2)]))
    scan=AsyncMock(return_value={'sources':{}})
    monkeypatch.setattr(services,'scan_for_user',scan)
    save=AsyncMock(side_effect=[RuntimeError('private database credentials'),None])
    monkeypatch.setattr(services.repo,'set_state',save)
    asyncio.run(services.scan_all(object()))
    assert scan.await_count==2
    assert save.await_count==2
    assert 'private database credentials' not in caplog.text


def test_fallback_observation_does_not_hide_later_connection_timeout(monkeypatch):
    from app.sources.diagnostics import diagnostic
    class HH:
        source_id='hh'
        name='HeadHunter'
        async def discover(self,context):
            self.fallback_count=1
            self.discovery_diagnostics=[diagnostic('HTTP_403_FORBIDDEN',stage='http',action='fallback')]
            raise httpx.ConnectTimeout('private fallback URL')
    configure_scan(monkeypatch,{'hh':lambda *args:HH()})
    alerts=AsyncMock()
    monkeypatch.setattr(services,'notify_chat',alerts)
    summary=asyncio.run(services.scan_for_user(object(),7))
    info=summary['sources']['hh']
    assert info['status']=='failed'
    assert info['fallback']==1
    assert {item['code'] for item in info['diagnostics']}=={'HTTP_403_FORBIDDEN','NETWORK_CONNECT_TIMEOUT'}
    assert alerts.await_count==2
    assert any('NETWORK_CONNECT_TIMEOUT' in call.args[2] for call in alerts.await_args_list)
    assert 'private fallback URL' not in str(summary)


def test_hh_certificate_failure_is_not_hidden_by_quiet_cooldown(monkeypatch):
    class HH:
        source_id='hh'
        name='HeadHunter'
        async def discover(self,context):
            exc=httpx.ConnectError('secret request URL')
            exc.__cause__=ssl.SSLCertVerificationError('secret certificate data')
            raise exc
    configure_scan(monkeypatch,{'hh':lambda *args:HH()})
    alerts=AsyncMock()
    monkeypatch.setattr(services,'notify_chat',alerts)
    summary=asyncio.run(services.scan_for_user(object(),7))
    assert summary['sources']['hh']['status']=='failed'
    assert alerts.await_count==1
    assert 'TLS_VALIDATION_FAILED' in alerts.await_args.args[2]
    assert 'secret' not in alerts.await_args.args[2]
    assert services._HH_CONNECT_RETRY_AFTER>0


def test_cached_discovery_does_not_merge_independent_profile_processing_failures(monkeypatch):
    calls=[]
    class Remote:
        source_id=name='remoteok'
        async def discover(self,context):
            calls.append(1)
            return [NormalizedJob(source='remoteok',source_job_id='1',title='DevOps')]
    configure_scan(monkeypatch,{'remoteok':Remote})
    original=services._user_context
    async def context(user_id):
        user,profile,searches=await original(user_id)
        searches.append(SimpleNamespace(id=12,name='Relocation-first',settings={'queries':['DevOps']}))
        return user,profile,searches
    monkeypatch.setattr(services,'_user_context',context)
    monkeypatch.setattr(services,'ingest_and_match',AsyncMock(side_effect=RuntimeError('private data')))
    alerts=AsyncMock()
    monkeypatch.setattr(services,'notify_chat',alerts)
    summary=asyncio.run(services.scan_for_user(object(),7))
    info=summary['sources']['remoteok']
    assert len(calls)==1
    assert info['processing_errors']==2
    assert len(info['diagnostics'])==2
    assert len({item['observation_id'] for item in info['diagnostics']})==2
    assert alerts.await_count==1
    assert 'Career-first / Relocation-first' in alerts.await_args.args[2]


def test_partial_metadata_survives_generic_source_cache_without_double_counting(monkeypatch):
    from app.sources.diagnostics import classify_source_error
    class Remote:
        source_id=name='remoteok'
        async def discover(self,context):
            self.partial_failures=1
            self.retry_count=2
            self.discovery_diagnostics=[classify_source_error(httpx.ReadTimeout('private'),action='continue_partial')]
            return [NormalizedJob(source='remoteok',source_job_id='1',title='DevOps')]
    configure_scan(monkeypatch,{'remoteok':Remote})
    original=services._user_context
    async def context(user_id):
        user,profile,searches=await original(user_id)
        searches.append(SimpleNamespace(id=12,name='Relocation-first',settings={'queries':['DevOps']}))
        return user,profile,searches
    monkeypatch.setattr(services,'_user_context',context)
    monkeypatch.setattr(services,'ingest_and_match',AsyncMock(return_value={'processed':1}))
    monkeypatch.setattr(services,'notify_chat',AsyncMock())
    summary=asyncio.run(services.scan_for_user(object(),7))
    info=summary['sources']['remoteok']
    assert info['partial_failures']==1
    assert info['partial_attempts']==2
    assert info['retry']==2
    assert len(info['diagnostics'])==1
    assert info['diagnostics'][0]['profiles']==['Career-first','Relocation-first']
    assert summary['searches']['12']['sources']['remoteok']['cache']
    assert summary['searches']['12']['sources']['remoteok']['status']=='partial'


def test_progress_callback_error_does_not_log_sensitive_payload(monkeypatch,caplog):
    class Remote:
        source_id=name='remoteok'
        async def discover(self,context):
            return []
    configure_scan(monkeypatch,{'remoteok':Remote})
    callback=AsyncMock(side_effect=RuntimeError('https://private.test/?token=private-value'))
    summary=asyncio.run(services.scan_for_user(object(),7,callback))
    assert summary['sources']['remoteok']['status']=='success'
    assert 'scan progress update failed (RuntimeError)' in caplog.text
    assert 'private-value' not in caplog.text
