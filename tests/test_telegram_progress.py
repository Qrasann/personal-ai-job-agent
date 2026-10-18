import asyncio
import json
from types import SimpleNamespace
from unittest.mock import AsyncMock

from aiogram.enums import MessageEntityType
import pytest

from app.telegram import handlers
from app.telegram.multicommand import (
    build_child_message,
    parse_multi_commands,
)


class FakeParentMessage:
    def __init__(self, text: str):
        self.text = text
        self.entities = [
            SimpleNamespace(
                type=MessageEntityType.BOT_COMMAND,
                offset=0,
                length=8,
            )
        ]

    def model_copy(self, *, update):
        return SimpleNamespace(**update)


class ProgressMessage:
    def __init__(self):
        self.edits = []

    async def edit_text(self, text, **kwargs):
        self.edits.append((text, kwargs))


class IncomingMessage:
    def __init__(self, text: str):
        self.text = text
        self.answers = []
        self.progress = ProgressMessage()

    async def answer(self, text, **kwargs):
        self.answers.append((text, kwargs))
        return self.progress


def test_parse_multi_commands_keeps_each_command_once():
    text = "/job 24\n/compare 24\n/job 25\n/compare 25"
    assert parse_multi_commands(text) == [
        "/job 24",
        "/compare 24",
        "/job 25",
        "/compare 25",
    ]


def test_build_child_message_replaces_stale_entities():
    child = build_child_message(
        FakeParentMessage("/version\n/compare 24"),
        "/compare 24",
    )

    assert child.text == "/compare 24"
    assert len(child.entities) == 1

    entity = child.entities[0]
    assert entity.type == MessageEntityType.BOT_COMMAND
    assert entity.offset == 0
    assert entity.length == len("/compare")


def test_multi_command_dispatches_each_child_once(monkeypatch):
    calls = []

    async def fake_propagate(event_type, child_message, **kwargs):
        calls.append((event_type, child_message.text))

    monkeypatch.setattr(
        handlers.router,
        "propagate_event",
        fake_propagate,
    )

    message = FakeParentMessage(
        "/job 24\n/compare 24\n/job 25\n/compare 25"
    )

    asyncio.run(
        handlers.multi_command(
            message,
            bot=object(),
        )
    )

    assert calls == [
        ("message", "/job 24"),
        ("message", "/compare 24"),
        ("message", "/job 25"),
        ("message", "/compare 25"),
    ]


def test_compare_command_shows_progress_then_edits_same_message(monkeypatch):
    async def fake_require_user(message):
        return SimpleNamespace(id=7)

    async def fake_comparison(user_id, job_id):
        assert user_id == 7
        assert job_id == 24
        return {"job": SimpleNamespace(id=24)}

    monkeypatch.setattr(
        handlers,
        "_require_user",
        fake_require_user,
    )
    monkeypatch.setattr(
        handlers,
        "get_vacancy_comparison",
        fake_comparison,
    )
    monkeypatch.setattr(
        handlers,
        "render_fact_comparison",
        lambda payload: "FINAL COMPARE",
    )

    message = IncomingMessage("/compare 24")
    asyncio.run(handlers.compare_job(message))

    assert [x[0] for x in message.answers] == [
        "⏳ Сравниваю требования вакансии с Candidate Facts…"
    ]
    assert [x[0] for x in message.progress.edits] == [
        "FINAL COMPARE"
    ]


def test_job_command_shows_progress_then_edits_same_message(monkeypatch):
    async def fake_require_user(message):
        return SimpleNamespace(id=7)

    async def fake_details(user_id, job_id):
        assert user_id == 7
        assert job_id == 24
        return {"job": SimpleNamespace(id=24)}

    monkeypatch.setattr(
        handlers,
        "_require_user",
        fake_require_user,
    )
    monkeypatch.setattr(
        handlers,
        "get_vacancy_details",
        fake_details,
    )
    monkeypatch.setattr(
        handlers,
        "render_job_summary",
        lambda payload: "FINAL JOB",
    )
    monkeypatch.setattr(
        handlers,
        "vacancy_details_keyboard",
        lambda job_id: None,
    )

    message = IncomingMessage("/job 24")
    asyncio.run(handlers.job_details(message))

    assert [x[0] for x in message.answers] == [
        "⏳ Загружаю полное описание вакансии…"
    ]
    assert [x[0] for x in message.progress.edits] == [
        "FINAL JOB"
    ]


def test_scan_command_shows_progress_then_edits_same_message(monkeypatch):
    async def fake_require_user(message):
        return SimpleNamespace(id=7)

    async def fake_scan(bot, user_id, progress_callback=None, force_refresh=False, on_start=None):
        await on_start()
        assert user_id == 7
        assert force_refresh is True
        assert progress_callback is not None
        await progress_callback("⏳ HH: поиск…")
        await progress_callback("⏳ HH: найдено 2 · анализ 2/2")
        await asyncio.sleep(0)
        return {
            "sources": {
                "hh": {
                    "found": 2,
                    "cache": False,
                }
            },
            "searches": {
                "11": {
                    "name": "Career-first",
                    "processed": 1,
                    "qualified": 1,
                    "stretch": 0,
                },
                "12": {
                    "name": "Relocation-first",
                    "processed": 1,
                    "qualified": 0,
                    "stretch": 1,
                },
            },
            "processed": 2,
            "qualified": 1,
            "stretch": 1,
            "filtered": 0,
            "notified": 1,
            "duplicate": 0,
        }

    monkeypatch.setattr(
        handlers,
        "_require_user",
        fake_require_user,
    )
    monkeypatch.setattr(
        handlers,
        "coordinated_scan_for_user",
        fake_scan,
    )
    monkeypatch.setattr(handlers.repo, "get_state", AsyncMock(return_value="{}"))
    monkeypatch.setattr(handlers.repo, "set_state", AsyncMock())

    message = IncomingMessage("/scan")
    asyncio.run(
        handlers.scan(
            message,
            bot=object(),
        )
    )

    assert [x[0] for x in message.answers] == [
        "⏳ Ищу вакансии по активным источникам…"
    ]
    assert len(message.progress.edits) == 2
    assert "⏱ Прошло:" in message.progress.edits[0][0]
    assert "Проход поиска завершён" in message.progress.edits[-1][0]
    assert "hh: готово · 2 вакансий (" in message.progress.edits[-1][0]
    assert "Career-first: 1 обработано, 1 Good, 0 Stretch" in message.progress.edits[-1][0]
    assert "Relocation-first: 1 обработано, 0 Good, 1 Stretch" in message.progress.edits[-1][0]
    assert "🟢 Good: 1" in message.progress.edits[-1][0]
    assert "🟡 Stretch: 1" in message.progress.edits[-1][0]
    assert "⚪ Отфильтровано: 0" in message.progress.edits[-1][0]
    assert "📨 Новых уведомлений: 1" in message.progress.edits[-1][0]


def test_scan_status_renders_persisted_source_timing(monkeypatch):
    monkeypatch.setattr(handlers, "_require_user", AsyncMock(return_value=SimpleNamespace(id=7)))
    monkeypatch.setattr(
        handlers.repo,
        "get_state",
        AsyncMock(return_value='{"status":"completed","started_at":"2026-10-11 10:00 UTC","finished_at":"2026-10-11 10:01 UTC","stage":"Готово","summary":{"sources":{"jobbank":{"found":2,"duration_ms":12000}}}}'),
    )
    message = IncomingMessage("/scanstatus")

    asyncio.run(handlers.scan_status(message))

    rendered = message.answers[0][0]
    assert "completed" in rendered
    assert "2026-10-11 10:01 UTC" in rendered
    assert "Источники: ✅ 1 · ⚠️ 0 · ❌ 0 · ⏸ 0" in rendered
    assert "jobbank: готово" not in rendered
    keyboard = message.answers[0][1]["reply_markup"]
    assert keyboard.inline_keyboard[0][0].callback_data == "scanstatus:details"


def test_scan_and_status_dense_emoji_diagnostics_fit_telegram(monkeypatch):
    from xml.etree import ElementTree

    stored = {}
    name = "🚀" * 65 + " <&>"
    summary = {
        "sources": {str(n): {
            "name": "Remote API", "found": 3, "partial": True,
            "diagnostics": [{"code": "NETWORK_CONNECT_TIMEOUT", "profiles": [name]}],
        } for n in range(12)},
        "searches": {str(n): {"name": name, "processed": 3} for n in range(6)},
    }

    async def set_state(user_id, key, value):
        stored[key] = value

    monkeypatch.setattr(handlers, "_ACTIVE_SCAN_TASKS", {})
    monkeypatch.setattr(handlers, "_require_user", AsyncMock(return_value=SimpleNamespace(id=7)))
    monkeypatch.setattr(handlers, "coordinated_scan_for_user", AsyncMock(return_value=summary))
    monkeypatch.setattr(handlers.repo, "get_state", AsyncMock(side_effect=lambda uid, key, default: stored.get(key, default)))
    monkeypatch.setattr(handlers.repo, "set_state", set_state)
    scan_message, status_message = IncomingMessage("/scan"), IncomingMessage("/scanstatus")

    async def scenario():
        await handlers.scan(scan_message, bot=object())
        await handlers.scan_status(status_message)

    asyncio.run(scenario())
    rendered, kwargs = scan_message.progress.edits[-1]
    assert len(rendered.encode("utf-16-le")) // 2 <= 4096
    assert kwargs["parse_mode"] == "HTML"
    ElementTree.fromstring("<root>" + rendered + "</root>")
    assert "NETWORK_CONNECT_TIMEOUT" in rendered
    assert "Профили поиска" in rendered
    assert "🚀" in rendered
    compact, compact_kwargs = status_message.answers[0]
    for rendered, kwargs in ((compact, compact_kwargs),):
        assert len(rendered.encode("utf-16-le")) // 2 <= 4096
        assert kwargs["parse_mode"] == "HTML"
        ElementTree.fromstring("<root>" + rendered + "</root>")
        assert "Источники: ✅ 0 · ⚠️ 12 · ❌ 0 · ⏸ 0" in rendered
        assert "NETWORK_CONNECT_TIMEOUT" not in rendered
    # Display truncation must not lose the diagnostic history.
    assert json.loads(stored["scan_dashboard"])["summary"] == summary


@pytest.mark.parametrize("skip_reason", ["ConnectError", "connection cooldown"])
def test_scan_and_persisted_status_show_quiet_source_skip(monkeypatch, skip_reason):
    stored = "{}"
    summary = {
        "sources": {
            "hh": {"skipped": skip_reason, "duration_ms": 2000},
            "remoteok": {"found": 0, "cache": False, "duration_ms": 1000},
            "jobbank": {"error": "ReadTimeout", "duration_ms": 3000},
        }
    }

    async def set_state(user_id, key, value):
        nonlocal stored
        assert (user_id, key) == (7, "scan_dashboard")
        stored = value

    monkeypatch.setattr(handlers, "_ACTIVE_SCAN_TASKS", {})
    monkeypatch.setattr(handlers, "_require_user", AsyncMock(return_value=SimpleNamespace(id=7)))
    monkeypatch.setattr(handlers, "coordinated_scan_for_user", AsyncMock(return_value=summary))
    monkeypatch.setattr(handlers.repo, "get_state", AsyncMock(side_effect=lambda *a: stored))
    monkeypatch.setattr(handlers.repo, "set_state", set_state)

    scan_message = IncomingMessage("/scan")
    status_message = IncomingMessage("/scanstatus")

    async def scenario():
        await handlers.scan(scan_message, bot=object())
        await handlers.scan_status(status_message)

    asyncio.run(scenario())

    completed = scan_message.progress.edits[-1][0]
    persisted = status_message.answers[0][0]
    assert "• hh: пропущен" in completed
    assert "hh: 0" not in completed
    assert skip_reason not in completed
    assert "• jobbank: ошибка" in completed
    assert "Источники: ✅ 1 · ⚠️ 0 · ❌ 1 · ⏸ 1" in persisted
    assert skip_reason not in persisted
    assert "remoteok: готово · 0 вакансий (1.0 с)" in completed
    assert "remoteok: готово" not in persisted
    assert json.loads(stored)["summary"] == summary
    assert len(scan_message.answers) == 1
    assert handlers._ACTIVE_SCAN_TASKS == {}


def test_scan_and_status_keep_successful_count_for_partial_source(monkeypatch):
    summary = {
        "sources": {
            "hh": {"found": 4, "cache": False, "duration_ms": 1000, "partial": True},
            "eures": {"found": 3, "cache": False, "duration_ms": 2500, "partial": True, "partial_failures": 2},
            "remoteok": {"found": 2, "cache": True, "duration_ms": 0},
        }
    }
    state = json.dumps({"status": "completed", "summary": summary})
    monkeypatch.setattr(handlers, "_ACTIVE_SCAN_TASKS", {})
    monkeypatch.setattr(handlers, "_require_user", AsyncMock(return_value=SimpleNamespace(id=7)))
    monkeypatch.setattr(handlers, "coordinated_scan_for_user", AsyncMock(return_value=summary))
    monkeypatch.setattr(handlers.repo, "get_state", AsyncMock(return_value=state))
    monkeypatch.setattr(handlers.repo, "set_state", AsyncMock())
    scan_message = IncomingMessage("/scan")
    status_message = IncomingMessage("/scanstatus")

    async def scenario():
        await handlers.scan(scan_message, bot=object())
        await handlers.scan_status(status_message)

    asyncio.run(scenario())

    completed = scan_message.progress.edits[-1][0]
    persisted = status_message.answers[0][0]
    assert "hh: частично · 4 вакансий (1.0 с)" in completed
    assert "Источники: ✅ 1 · ⚠️ 2 · ❌ 0 · ⏸ 0" in persisted
    assert "eures: частично · 3 вакансий (2.5 с) · сбои: 2" in completed
    assert "eures: частично" not in persisted
    assert "remoteok: готово · 2 вакансий (0.0 с) · кэш" in completed
    assert "remoteok: готово" not in persisted
    assert completed.count("частично") == 2
    assert "hh: ошибка" not in completed
    assert "hh: пропущен" not in completed


def test_scanstatus_shows_failure_count_when_all_eures_requests_fail(monkeypatch):
    state = json.dumps({"status": "completed", "summary": {"sources": {
        "eures": {"error": "HTTP 503", "duration_ms": 2500, "partial_failures": 6},
    }}})
    monkeypatch.setattr(handlers, "_require_user", AsyncMock(return_value=SimpleNamespace(id=7)))
    monkeypatch.setattr(handlers.repo, "get_state", AsyncMock(return_value=state))
    message = IncomingMessage("/scanstatus")

    asyncio.run(handlers.scan_status(message))

    assert "Источники: ✅ 0 · ⚠️ 0 · ❌ 1 · ⏸ 0" in message.answers[0][0]


def test_cancel_stops_only_the_active_manual_scan(monkeypatch):
    async def scenario():
        monkeypatch.setattr(handlers, "_require_user", AsyncMock(return_value=SimpleNamespace(id=7)))
        monkeypatch.setattr(handlers.repo, "set_state", AsyncMock())
        waiting = asyncio.Event()
        task = asyncio.create_task(waiting.wait())
        handlers._ACTIVE_SCAN_TASKS[7] = task
        await asyncio.sleep(0)
        message = IncomingMessage("/cancel")
        await handlers.cancel(message)
        try:
            await task
        except asyncio.CancelledError:
            pass
        assert task.cancelled()
        assert "Останавливаю текущий скан" in message.answers[0][0]
        handlers._ACTIVE_SCAN_TASKS.pop(7, None)

    asyncio.run(scenario())


@pytest.mark.parametrize('manual_status,manual_time,expected',[
    ('running','2026-10-14 10:00:00 UTC','manual'),
    ('completed','2026-10-14 10:00:00 UTC','scheduled'),
    ('completed','2026-10-14 14:00:00 UTC','manual'),
])
def test_scanstatus_selects_latest_without_overwriting_active_manual(monkeypatch,manual_status,manual_time,expected):
    manual={'status':manual_status,'started_at':manual_time,'stage':'manual','summary':{'sources':{}}}
    scheduled={'kind':'scheduled','status':'partial','started_at':'2026-10-14 12:00:00 UTC','stage':'scheduled',
               'summary':{'sources':{'remoteok':{'found':1,'partial':True,'error':None,'diagnostics':[
                   {'code':'NETWORK_CONNECT_TIMEOUT','profiles':['Relocation-first']}]}}}}
    monkeypatch.setattr(handlers,'_require_user',AsyncMock(return_value=SimpleNamespace(id=7)))
    monkeypatch.setattr(handlers.repo,'get_state',AsyncMock(side_effect=lambda user,key,*args:json.dumps(scheduled if key=='scheduled_scan_dashboard' else manual)))
    message=IncomingMessage('/scanstatus')
    asyncio.run(handlers.scan_status(message))
    text=message.answers[0][0]
    detail = handlers._scan_status_details(scheduled if expected == 'scheduled' else manual)
    assert f'Этап: {expected}' in detail
    if expected=='scheduled':
        assert 'Плановый поиск' in text
        assert 'NETWORK_CONNECT_TIMEOUT' not in text
        assert 'NETWORK_CONNECT_TIMEOUT' in detail
        assert 'Relocation-first' in detail
    else:
        assert 'Плановый поиск' not in text
        assert 'NETWORK_CONNECT_TIMEOUT' not in detail


def test_scanstatus_source_names_are_escaped_once_and_legacy_errors_are_safe(monkeypatch):
    state={'status':'completed','summary':{'sources':{'hh':{'name':'HH <API> & public','error':'&#x27;found&#x27;'}}}}
    monkeypatch.setattr(handlers,'_require_user',AsyncMock(return_value=SimpleNamespace(id=7)))
    monkeypatch.setattr(handlers.repo,'get_state',AsyncMock(side_effect=lambda user,key,*args:json.dumps(state) if key=='scan_dashboard' else '{}'))
    message=IncomingMessage('/scanstatus')
    asyncio.run(handlers.scan_status(message))
    text=handlers._scan_status_details(state)
    options=message.answers[0][1]
    assert 'HH &lt;API&gt; &amp; public' in text
    assert '&amp;lt;' not in text
    assert '&#x27;found' not in text
    assert 'SOURCE_SUMMARY_MISSING_FIELD' in text
    assert options['parse_mode']=='HTML'
    assert '<b>failed</b>' in text


def test_dense_partial_scan_fits_telegram_and_keeps_valid_html(monkeypatch):
    from html.parser import HTMLParser
    class Tags(HTMLParser):
        def __init__(self):
            super().__init__()
            self.tags=[]
        def handle_starttag(self,tag,attrs):
            self.tags.append(tag)
        def handle_endtag(self,tag):
            assert self.tags.pop()==tag
    summary={'sources':{f'source_{n}':{'found':3,'partial':True,'name':'<API> & feed',
             'diagnostics':[{'code':code,'profiles':['Career-first','Relocation-first']} for code in
             ['NETWORK_CONNECT_TIMEOUT','HTTP_403_FORBIDDEN','HTTP_429_RATE_LIMITED','HTTP_5XX_SERVER_ERROR']]}
             for n in range(13)}}
    monkeypatch.setattr(handlers,'_ACTIVE_SCAN_TASKS',{})
    monkeypatch.setattr(handlers,'_require_user',AsyncMock(return_value=SimpleNamespace(id=7)))
    monkeypatch.setattr(handlers,'coordinated_scan_for_user',AsyncMock(return_value=summary))
    monkeypatch.setattr(handlers.repo,'get_state',AsyncMock(return_value='{}'))
    monkeypatch.setattr(handlers.repo,'set_state',AsyncMock())
    message=IncomingMessage('/scan')
    asyncio.run(handlers.scan(message,bot=object()))
    text,options=message.progress.edits[-1]
    assert len(text)<=4096
    assert 'неполными результатами' in text
    assert '…' in text
    parser=Tags()
    parser.feed(text)
    assert not parser.tags
    assert options['parse_mode']=='HTML'


def test_scanstatus_sanitizes_legacy_failed_stage(monkeypatch):
    state={'status':'failed','stage':'https://private.test/?token=private-value'}
    monkeypatch.setattr(handlers,'_require_user',AsyncMock(return_value=SimpleNamespace(id=7)))
    monkeypatch.setattr(handlers.repo,'get_state',AsyncMock(side_effect=lambda user,key,*args:json.dumps(state) if key=='scan_dashboard' else '{}'))
    message=IncomingMessage('/scanstatus')
    asyncio.run(handlers.scan_status(message))
    compact = message.answers[0][0]
    detail = handlers._scan_status_details(state)
    assert 'private-value' not in compact
    assert 'private-value' not in detail
    assert 'SOURCE_PROCESSING_FAILED' in detail
