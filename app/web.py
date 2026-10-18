"""Private, owner-scoped web workspace over the existing PostgreSQL workflow."""

from __future__ import annotations

import asyncio
import html
import logging
import os
import secrets
import time
from datetime import date
from urllib.parse import quote, urlsplit

from aiohttp import web
from aiohttp.web_request import FileField
from aiogram import Bot

from app.candidates.fact_types import ALLOWED_EXPERIENCE_TYPES
from app.candidates.import_review import plan_fact_import
from app.candidates.importer import MAX_DOCUMENT_BYTES, ResumeImportError, extract_resume_text, guess_language, propose_facts, resume_fingerprint, review_proposals
from app.config import settings
from app.database import repository as repo
from app.geo.countries import normalize_country
from app.search.preferences import discovery_queries, relocation_first_allows, search_config
from app.services import ScanAlreadyRunning, coordinated_scan_for_user, get_vacancy_details
from app.sources.registry import IMPLEMENTED
from app.telegram.handlers import _prepare_saved_preview, _save_scan_dashboard
from app.telegram.vacancy_view import render_application_export, render_job_details

log = logging.getLogger(__name__)
PAGES = ("dashboard", "search", "jobs", "review", "profiles", "sources", "relocation", "cv", "applications")
LABELS = ("Dashboard", "Search", "Jobs", "Review", "Profiles", "Sources", "Relocation", "CV", "Applications")
SCAN_SOURCES = IMPLEMENTED - {"telegram", "jobs_ge"}
CV_PREVIEW_TTL = 15 * 60


def e(value: object) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)


def safe_link(value: str | None) -> str:
    try:
        parsed = urlsplit(value or "")
        if not value or len(value) > 2048 or any(c.isspace() or c == "\\" for c in value):
            return ""
        return value if parsed.scheme == "https" and parsed.hostname and not parsed.username and not parsed.password and (parsed.port is None or 1 <= parsed.port <= 65535) else ""
    except ValueError:
        return ""


def layout(page: str, body: str, *, notice: str = "") -> web.Response:
    nav = "".join(f'<a class="{"active" if page == key else ""}" href="/{key}">{label}</a>' for key, label in zip(PAGES, LABELS))
    message = f'<p class="notice">{e(notice)}</p>' if notice else ""
    document = f'''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(page.title())} · Job Agent</title><style>
:root{{font-family:system-ui,sans-serif;color:#17212f;background:#f3f5f8}}*{{box-sizing:border-box}}body{{margin:0}}header{{background:#10243b;color:white;padding:18px 24px}}header strong{{font-size:1.2rem}}nav{{display:flex;gap:6px;overflow:auto;padding:10px 20px;background:white;border-bottom:1px solid #dce2e9}}nav a{{white-space:nowrap;padding:9px 12px;border-radius:8px;color:#29445d;text-decoration:none}}nav a.active,nav a:hover{{background:#dfeaf7}}main{{max-width:1050px;margin:24px auto;padding:0 18px}}section,.card{{background:white;border:1px solid #dce2e9;border-radius:12px;padding:18px;margin:14px 0}}h1{{margin:0 0 18px}}h2{{font-size:1.15rem}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px}}.grid .card{{margin:0}}.muted{{color:#5a6876}}.notice{{background:#e7f3e7;padding:12px;border-radius:8px}}.error{{color:#a32525}}a{{color:#145b9b}}button{{background:#154e81;color:white;border:0;border-radius:7px;padding:9px 13px;cursor:pointer}}button.secondary{{background:#627385}}form{{display:inline-block;margin:4px 6px 4px 0}}input,select,textarea{{font:inherit;padding:8px;border:1px solid #aebbc9;border-radius:6px;max-width:100%}}input[type=text]{{min-width:230px}}textarea{{width:100%;min-height:90px}}label{{display:block;margin:9px 0}}pre{{white-space:pre-wrap;overflow-wrap:anywhere}}.score{{font-weight:bold;color:#116b41}}.row{{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap}}small{{color:#637080}}
</style></head><body><header><strong>Personal AI Job Agent</strong> <span class="muted">· private workspace</span></header><nav>{nav}</nav><main><h1>{e(page.title())}</h1>{message}{body}</main></body></html>'''
    return web.Response(text=document, content_type="text/html", headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff", "Content-Security-Policy": "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'", "Referrer-Policy": "no-referrer"})


def form(action: str, label: str, fields: str = "", *, secondary: bool = False) -> str:
    return f'<form method="post" action="{e(action)}"><input type="hidden" name="csrf" value="{{csrf}}">{fields}<button class="{"secondary" if secondary else ""}">{e(label)}</button></form>'


async def owner(request: web.Request):
    user = await repo.get_user_by_chat(settings.telegram_admin_chat_id.strip())
    if not user or not user.is_active:
        raise web.HTTPServiceUnavailable(text="Owner profile unavailable")
    return user


async def profile_and_searches(user):
    profile = await repo.active_profile(user.id)
    searches = await repo.list_search_profiles(profile.id) if profile else []
    return profile, searches


def selected_search(searches, raw: str):
    return next((s for s in searches if str(s.id) == raw), None)


async def page_content(request: web.Request, user, page: str) -> str:
    profile, searches = await profile_and_searches(user)
    if not profile:
        return '<section class="error">Активный профиль не найден. Создай его через Telegram /start.</section>'
    if page == "dashboard":
        stats = await repo.stats(user.id)
        scan = await repo.get_state(user.id, "scan_dashboard", "")
        cards = "".join(f'<div class="card"><h2>{e(k)}</h2><strong>{e(v)}</strong></div>' for k, v in stats.items())
        return f'<div class="grid">{cards}</div><section><h2>Последний ручной поиск</h2><pre>{e(scan or "Пока не запускался")}</pre><a href="/search">Открыть поиск</a></section>'
    if page == "search":
        rows = []
        for s in searches:
            cfg = search_config(s.settings)
            rows.append(f'<div class="card"><h2>{e(s.name)}</h2><p>Стратегия: {e(cfg.get("search_strategy"))}</p><p>Запросы: {e(", ".join(discovery_queries(cfg, profile.target_role)))}</p><p>Страны: {e(", ".join(cfg.get("target_countries") or []) or "не заданы")}</p></div>')
        state = request.app["scan_state"].get(user.id, "idle")
        return f'<section><p>Поиск выполняется по всем включённым профилям и их реальным источникам.</p>{form("/action/scan", "Запустить поиск") if state != "running" else "⏳ Поиск выполняется"}<p>Состояние: {e(state)} · <a href="/search">обновить</a></p></section><div class="grid">{"".join(rows)}</div>'
    if page in {"jobs", "review"}:
        kind = request.query.get("scope", "")
        selected = next((s for s in searches if s.kind == kind), None)
        if page == "review":
            matches = await repo.review_matches(user.id, 30)
        else:
            threshold = int((selected.settings or {}).get("notify_min_score", 65)) if selected else 65
            below = request.query.get("below") == "1"
            matches = await repo.latest_matches(
                user.id, 80 if kind == "relocation" else 50,
                search_profile_id=selected.id if selected else None,
                include_filtered=below,
                min_score=1 if below else threshold,
                max_score=threshold - 1 if below else None,
            )
            if kind == "relocation" and selected:
                matches = [(match, job) for match, job in matches if relocation_first_allows(job, selected.settings, current_country=user.current_country)]
        filters = '<p><a href="/jobs">Все от порога</a> · <a href="/jobs?scope=career">Career-first</a> · <a href="/jobs?scope=relocation">Relocation-first</a> · <a href="/jobs?scope=career&amp;below=1">Career ниже порога</a> · <a href="/jobs?scope=relocation&amp;below=1">Relocation ниже порога</a></p>' if page == "jobs" else ""
        rows = []
        for match, job in matches:
            buttons = form("/action/match", "Сохранить", f'<input type="hidden" name="id" value="{match.id}"><input type="hidden" name="status" value="saved">') if match.status not in {"saved", "prepared"} else ""
            buttons += form("/action/match", "Пропустить", f'<input type="hidden" name="id" value="{match.id}"><input type="hidden" name="status" value="skipped">', secondary=True) if match.status not in {"skipped", "prepared"} else ""
            buttons += form("/action/prepare", "Подготовить пакет", f'<input type="hidden" name="id" value="{match.id}">')
            rows.append(f'<section><div class="row"><h2><a href="/job/{job.id}?search={match.search_profile_id}">{e(job.title)} · {e(job.company)}</a></h2><span class="score">{match.total_score}/100</span></div><p>{e(job.city or "")} {e(job.country or "")} · {e(match.status)} · <a href="/job/{job.id}?search={match.search_profile_id}">Источник и evidence</a></p><p>{e(match.reason)}</p>{buttons}</section>')
        empty = '<section>Нет результатов в выбранном диапазоне. Проверь настройки и /scanstatus в Telegram.</section>'
        return filters + ("".join(rows) or empty)
    if page == "profiles":
        facts = await repo.list_facts(profile.id)
        types = "".join(f'<option value="{e(kind)}">{e(kind)}</option>' for kind in ("unknown", "lab", "learning", "commercial"))
        add_fact = form("/action/fact", "Добавить факт", f'<label>Утверждение <textarea name="value" maxlength="2000" required></textarea></label><label>Тип опыта <select name="experience_type">{types}</select></label><label>Основание <input name="evidence" type="text" maxlength="1000" required></label>')
        return f'<section><h2>{e(profile.name)}</h2><p>Целевая роль: {e(profile.target_role)} · Английский: {e(profile.english_level or "не задан")}</p>{form("/action/profile", "Сохранить роль", f"<input name='role' type='text' maxlength='256' value='{e(profile.target_role)}' required>")}</section><section><h2>Candidate Facts</h2><p>Добавляй только проверенные сведения. Тип commercial указывай лишь для реального оплачиваемого опыта.</p>{add_fact}</section><section><h2>Активные факты</h2>' + ("".join(f'<p>#{f.id} · {e(f.category)} · {e(f.experience_type)} · {e(f.value)}<br><small>{e(f.evidence)}</small></p>' for f in facts) or '<p>Фактов пока нет.</p>') + '</section>'
    if page in {"sources", "relocation"}:
        blocks = []
        for s in searches:
            cfg = search_config(s.settings)
            if page == "sources":
                disabled = set(cfg.get("disabled_sources") or [])
                checkboxes = "".join(f'<label><input type="checkbox" name="source" value="{e(source)}" {"" if source in disabled else "checked"}> {e(source)}</label>' for source in sorted(SCAN_SOURCES))
                blocks.append(f'<section><h2>{e(s.name)}</h2>{form("/action/sources", "Сохранить источники", f"<input type='hidden' name='search' value='{s.id}'>" + checkboxes)}</section>')
            else:
                blocks.append(f'<section><h2>{e(s.name)}</h2><p>Страны: {e(", ".join(cfg.get("target_countries") or []) or "не заданы")}</p><p>Relocation-запросы: {e(", ".join(cfg.get("relocation_queries") or []) or "не заданы")}</p>{form("/action/relocation", "Сохранить", f"<input type='hidden' name='search' value='{s.id}'><label>Коды стран через запятую <input name='countries' type='text' value='{e(', '.join(cfg.get('target_countries') or []))}'></label><label>Роли через запятую <input name='roles' type='text' value='{e(', '.join(cfg.get('relocation_queries') or []))}'></label>")}</section>')
        toggle = form("/action/parallel", "Включить Career-first и Relocation-first") if page == "relocation" and not any(s.kind == "relocation" for s in searches) else ""
        return toggle + ("".join(blocks) or '<section>Профили поиска отсутствуют.</section>')
    if page == "cv":
        resumes = await repo.list_resumes(profile.id)
        upload = '<section><h2>Импорт PDF, DOCX или TXT</h2><p>До 8 МБ. Сначала покажу извлечённый текст и предложенные факты; сохранение требует отдельного подтверждения.</p><form method="post" action="/action/cv_upload" enctype="multipart/form-data"><input type="hidden" name="csrf" value="{csrf}"><input type="file" name="document" accept=".pdf,.docx,.txt,.text" required><button>Показать предпросмотр</button></form></section>'
        add = '<section><h2>Добавить текст CV</h2><p>Текст сохраняется в профиль без автоматического подтверждения фактов.</p>' + form("/action/cv", "Сохранить CV", '<label>Название <input name="name" type="text" maxlength="128" required></label><label>Роль <input name="role" type="text" maxlength="256" required></label><label>Язык <select name="language"><option value="en">English</option><option value="ru">Русский</option></select></label><label>Текст CV <textarea name="content" required></textarea></label>') + '</section>'
        return upload + add + ("".join(f'<section><h2>#{r.id} · {e(r.name)}</h2><p>{e(r.role)} · {e(r.language)} · {e(r.source)}</p><details><summary>Текст резюме</summary><pre>{e(r.content)}</pre></details></section>' for r in resumes) or '<section>Резюме пока нет.</section>')
    if page == "applications":
        apps = await repo.list_applications(user.id, 50)
        return "".join(f'<section><h2>#{a.id} · {e((a.vacancy_snapshot or {}).get("title") or a.job_id)}</h2><p>{e(a.status)} · {e(a.source_id)}</p><a href="/application/{a.id}">Открыть пакет и историю</a></section>' for a in apps) or '<section>Подготовленных пакетов пока нет.</section>'
    raise web.HTTPNotFound()


async def run_scan(app: web.Application, user_id: int) -> None:
    app["scan_state"][user_id] = "running"
    try:
        summary = await coordinated_scan_for_user(
            app["bot"], user_id, force_refresh=True,
            on_start=lambda: _save_scan_dashboard(user_id, reset=True, status="running", stage="Web GUI: поиск запущен"),
        )
        app["scan_state"][user_id] = f'готово: {summary.get("processed", 0)} обработано, {summary.get("qualified", 0)} Good, {summary.get("stretch", 0)} Stretch'
        await _save_scan_dashboard(user_id, status="completed", stage="Web GUI: поиск завершён", summary=summary)
    except ScanAlreadyRunning:
        app["scan_state"][user_id] = "другой поиск уже выполняется"
    except Exception as exc:
        log.warning("web scan failed (%s)", type(exc).__name__)
        app["scan_state"][user_id] = f"ошибка: {type(exc).__name__}"
        await _save_scan_dashboard(user_id, status="failed", stage=f"Web GUI: {type(exc).__name__}")


def pending_cv(app: web.Application, token: str, user_id: int) -> dict | None:
    now = time.monotonic()
    for key, value in list(app["cv_pending"].items()):
        if now - value["created_at"] > CV_PREVIEW_TTL:
            app["cv_pending"].pop(key, None)
    pending = app["cv_pending"].get(token)
    return pending if pending and pending["user_id"] == user_id else None


def store_pending_cv(app: web.Application, user_id: int, pending: dict) -> str:
    pending_cv(app, "", user_id)
    rows = app["cv_pending"]
    owned = [(key, item) for key, item in rows.items() if item["user_id"] == user_id]
    if len(owned) >= 4:
        rows.pop(min(owned, key=lambda pair: pair[1]["created_at"])[0], None)
    if len(rows) >= 16:
        rows.pop(min(rows, key=lambda key: rows[key]["created_at"]), None)
    token = secrets.token_urlsafe(18)
    rows[token] = pending
    return token


async def cv_preview(request: web.Request) -> web.Response:
    user = await owner(request)
    pending = pending_cv(request.app, request.match_info["token"], user.id)
    if not pending:
        raise web.HTTPNotFound(text="CV preview expired")
    token = request.match_info["token"]
    overlap = {item.proposal: item for item in pending["overlaps"]}
    rows = []
    for index, proposal in enumerate(pending["proposals"]):
        conflict = overlap.get(proposal)
        options = ('<option value="keep">Оставить прежний факт</option><option value="add">Добавить отдельно</option><option value="update">Заменить прежний факт</option>' if conflict else '<option value="add">Добавить</option><option value="keep">Не добавлять</option>')
        existing = f'<br><small>Пересечение с #{conflict.existing_id}: {e(conflict.existing_value)}</small>' if conflict else ""
        rows.append(f'<label>#{index + 1} · {e(proposal.category)} · {e(proposal.value)}{existing}<br><select name="choice_{index}">{options}</select></label>')
    text = pending["content"]
    preview = e(text[:12_000]) + ("\n… Предпросмотр сокращён." if len(text) > 12_000 else "")
    body = f'<section><h2>Предпросмотр резюме</h2><p>Язык: {e(pending["language"])} · точных повторов фактов пропущено: {pending["duplicates_count"]}. Новые факты сохраняются с типом unknown; коммерческий опыт не выводится из файла автоматически.</p><details><summary>Извлечённый текст</summary><pre>{preview}</pre></details></section><section><h2>Выбор фактов</h2><form method="post" action="/action/cv_confirm"><input type="hidden" name="csrf" value="{{csrf}}"><input type="hidden" name="token" value="{e(token)}">{"".join(rows) or "<p>Новых предложенных фактов нет.</p>"}<button name="mode" value="resume">Сохранить только CV</button><button name="mode" value="facts">Сохранить CV и выбранные факты</button></form></section>'
    return layout("cv", body.replace("{csrf}", e(request.app["csrf"])))


async def dispatch(request: web.Request) -> web.StreamResponse:
    user = await owner(request)
    page = request.match_info.get("page", "dashboard")
    if page not in PAGES:
        raise web.HTTPNotFound()
    body = await page_content(request, user, page)
    return layout(page, body.replace("{csrf}", e(request.app["csrf"])), notice=request.query.get("notice", "")[:160])


async def action(request: web.Request) -> web.StreamResponse:
    user = await owner(request)
    data = await request.post()
    if not secrets.compare_digest(str(data.get("csrf", "")), request.app["csrf"]):
        raise web.HTTPForbidden()
    name = request.match_info["name"]
    profile, searches = await profile_and_searches(user)
    if not profile:
        raise web.HTTPConflict(text="Profile unavailable")
    target = "/dashboard"
    notice = "Сохранено"
    if name == "scan":
        target = "/search"
        if request.app["scan_state"].get(user.id) == "running":
            notice = "Поиск уже выполняется"
        else:
            request.app["scan_state"][user.id] = "running"
            task = asyncio.create_task(run_scan(request.app, user.id))
            request.app["scan_tasks"].add(task)
            task.add_done_callback(request.app["scan_tasks"].discard)
            notice = "Поиск запущен"
    elif name == "parallel":
        await repo.configure_parallel_search_profiles(profile.id, enabled=True)
        target = "/relocation"
    elif name == "profile":
        role = str(data.get("role", "")).strip()
        if not role or len(role) > 256:
            raise web.HTTPBadRequest(text="Invalid role")
        await repo.set_profile_target_role(profile.id, role)
        target = "/profiles"
    elif name == "fact":
        value = str(data.get("value", "")).strip()
        evidence = str(data.get("evidence", "")).strip()
        experience_type = str(data.get("experience_type", ""))
        if not value or not evidence or len(value) > 2000 or len(evidence) > 1000 or experience_type not in ALLOWED_EXPERIENCE_TYPES:
            raise web.HTTPBadRequest(text="Invalid candidate fact")
        await repo.add_fact(profile.id, value, category="experience", experience_type=experience_type, evidence=evidence, provenance="web_manual")
        target = "/profiles"
    elif name == "cv":
        cv_name = str(data.get("name", "")).strip()
        role = str(data.get("role", "")).strip()
        language = str(data.get("language", ""))
        content = str(data.get("content", "")).strip()
        if not cv_name or not role or not content or len(cv_name) > 128 or len(role) > 256 or len(content) > 100_000 or language not in {"en", "ru"}:
            raise web.HTTPBadRequest(text="Invalid CV")
        await repo.add_resume(profile.id, cv_name, language, role, content, source="manual")
        target = "/cv"
    elif name == "cv_upload":
        document = data.get("document")
        if not isinstance(document, FileField):
            raise web.HTTPBadRequest(text="CV file required")
        payload = document.file.read(MAX_DOCUMENT_BYTES + 1)
        try:
            content = extract_resume_text(document.filename or "", payload)
        except ResumeImportError as exc:
            target, notice = "/cv", str(exc)
        else:
            fingerprint = resume_fingerprint(content)
            if any(item.external_id == fingerprint for item in await repo.list_resumes(profile.id)):
                target, notice = "/cv", "Такое резюме уже импортировано"
            else:
                review = review_proposals(propose_facts(content), await repo.list_facts(profile.id))
                pending = {"user_id": user.id, "profile_id": profile.id, "content": content, "fingerprint": fingerprint, "language": guess_language(content), "role": profile.target_role or "", "proposals": review.new, "overlaps": review.overlaps, "duplicates_count": len(review.duplicates), "created_at": time.monotonic()}
                token = store_pending_cv(request.app, user.id, pending)
                target, notice = f"/cv/preview/{token}", "Проверь текст и факты перед сохранением"
    elif name == "cv_confirm":
        token = str(data.get("token", ""))
        pending = pending_cv(request.app, token, user.id)
        if not pending or pending["profile_id"] != profile.id:
            raise web.HTTPNotFound(text="CV preview expired")
        mode = str(data.get("mode", ""))
        if mode not in {"resume", "facts"}:
            raise web.HTTPBadRequest(text="Invalid CV choice")
        try:
            choices = {int(key[7:]): str(value) for key, value in data.items() if key.startswith("choice_")}
            plan = plan_fact_import(pending["proposals"], pending["overlaps"], choices)
        except (ValueError, TypeError):
            raise web.HTTPBadRequest(text="Invalid fact choices") from None
        if request.app["cv_pending"].pop(token, None) is not pending:
            raise web.HTTPConflict(text="CV preview already used")
        facts = [{"category": p.category, "value": p.value, "confidence": p.confidence, "section": p.section} for p in plan.additions] if mode == "facts" else []
        replacements = [{"existing_id": o.existing_id, "expected_value": o.existing_value, "category": o.proposal.category, "value": o.proposal.value, "confidence": o.proposal.confidence, "section": o.proposal.section} for o in plan.replacements] if mode == "facts" else []
        try:
            await repo.add_imported_resume_with_facts(profile.id, f"Imported resume {date.today():%Y-%m-%d}", pending["language"], pending["role"], pending["content"], pending["fingerprint"], facts, replacements=replacements)
        except repo.ResumeImportExists:
            notice = "Такое резюме уже импортировано"
        else:
            notice = "CV сохранено" + (" с выбранными фактами типа unknown" if mode == "facts" else " без новых фактов")
        target = "/cv"
    elif name in {"sources", "relocation"}:
        selected = selected_search(searches, str(data.get("search", "")))
        if not selected:
            raise web.HTTPNotFound()
        cfg = search_config(selected.settings)
        if name == "sources":
            enabled = set(data.getall("source", []))
            if not enabled.issubset(SCAN_SOURCES):
                raise web.HTTPBadRequest(text="Invalid source")
            cfg["disabled_sources"] = sorted((set(cfg.get("disabled_sources") or []) - SCAN_SOURCES) | (SCAN_SOURCES - enabled))
            cfg["enabled_sources"] = []
            target = "/sources"
        else:
            raw = [x.strip() for x in str(data.get("countries", "")).split(",") if x.strip()]
            countries = [normalize_country(x) for x in raw]
            if len(raw) > 30 or any(not x for x in countries):
                raise web.HTTPBadRequest(text="Invalid countries")
            roles = [x.strip() for x in str(data.get("roles", "")).split(",") if x.strip()]
            if len(roles) > 20 or any(len(x) > 100 for x in roles):
                raise web.HTTPBadRequest(text="Invalid roles")
            cfg["target_countries"] = list(dict.fromkeys(countries))
            cfg["relocation_queries"] = list(dict.fromkeys(roles))
            target = "/relocation"
        await repo.update_search_settings(selected.id, cfg)
    elif name in {"match", "prepare"}:
        try:
            match_id = int(data.get("id", ""))
        except (TypeError, ValueError):
            raise web.HTTPBadRequest() from None
        match = await repo.get_match(match_id)
        if not match or match.user_id != user.id:
            raise web.HTTPNotFound()
        if name == "prepare":
            try:
                await _prepare_saved_preview(match_id, user.id)
            except Exception as exc:
                log.warning("web prepare failed (%s)", type(exc).__name__)
                notice = "Подготовка не удалась. Проверь Applications перед повтором."
                target = "/review"
            else:
                target = "/applications"
                notice = "Пакет сохранён для ручной проверки"
        else:
            status = str(data.get("status", ""))
            if status not in {"saved", "skipped"} or match.status == "prepared":
                raise web.HTTPBadRequest()
            await repo.set_match_status(match_id, status)
            target = "/review"
    elif name == "application":
        try:
            app_id = int(data.get("id", ""))
        except (TypeError, ValueError):
            raise web.HTTPBadRequest() from None
        status = str(data.get("status", ""))
        if status not in repo.MANUAL_APPLICATION_STATUSES or not await repo.set_application_status(user.id, app_id, status):
            raise web.HTTPNotFound()
        target = "/applications"
        notice = "Статус отмечен вручную; это не отправляет заявку"
    else:
        raise web.HTTPNotFound()
    raise web.HTTPSeeOther(location=f"{target}?notice={quote(notice)}")


async def export_application(request: web.Request) -> web.Response:
    user = await owner(request)
    app_id = int(request.match_info["id"])
    application = await repo.get_application(user.id, app_id)
    if not application:
        raise web.HTTPNotFound()
    events = await repo.application_status_history(user.id, app_id)
    content = render_application_export(application, events)
    return web.Response(text=content, content_type="text/plain", charset="utf-8", headers={"Content-Disposition": f'attachment; filename="application-{app_id}.txt"', "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"})


async def application_detail(request: web.Request) -> web.Response:
    user = await owner(request)
    app_id = int(request.match_info["id"])
    application = await repo.get_application(user.id, app_id)
    if not application:
        raise web.HTTPNotFound()
    events = await repo.application_status_history(user.id, app_id)
    content = render_application_export(application, events)
    statuses = "".join(f'<option value="{e(status)}">{e(status)}</option>' for status in sorted(repo.MANUAL_APPLICATION_STATUSES))
    update = form("/action/application", "Отметить статус вручную", f'<input type="hidden" name="id" value="{app_id}"><select name="status">{statuses}</select>')
    body = f'<section><p>Статус: {e(application.status)}. Изменение статуса не отправляет заявку.</p>{update}<p><a href="/application/{app_id}/export">Скачать полный пакет</a></p><pre>{e(content[:100_000])}</pre>{"<p>Предпросмотр сокращён; экспорт содержит полный пакет.</p>" if len(content) > 100_000 else ""}</section>'
    return layout("applications", body.replace("{csrf}", e(request.app["csrf"])))


async def job_detail(request: web.Request) -> web.Response:
    user = await owner(request)
    try:
        job_id = int(request.match_info["id"])
        search_id = int(request.query["search"])
    except (KeyError, ValueError):
        raise web.HTTPBadRequest() from None
    try:
        payload = await get_vacancy_details(user.id, job_id, search_profile_id=search_id)
    except RuntimeError:
        raise web.HTTPNotFound() from None
    except Exception as exc:
        log.warning("web job detail failed (%s)", type(exc).__name__)
        raise web.HTTPServiceUnavailable(text="Vacancy details are temporarily unavailable") from None
    match = payload["match"]
    payload["url"] = safe_link(payload.get("url"))
    # The Telegram renderer already escapes posting text and restricts source links.
    detail = render_job_details(payload).replace("\n", "<br>")
    buttons = form("/action/match", "Сохранить", f'<input type="hidden" name="id" value="{match.id}"><input type="hidden" name="status" value="saved">') if match.status not in {"saved", "prepared"} else ""
    buttons += form("/action/prepare", "Подготовить пакет", f'<input type="hidden" name="id" value="{match.id}">')
    body = f'<section>{detail}<p>{buttons}</p></section>'
    return layout("jobs", body.replace("{csrf}", e(request.app["csrf"])))


@web.middleware
async def auth(request: web.Request, handler):
    app = request.app
    if request.path == "/login":
        return await handler(request)
    if not secrets.compare_digest(request.cookies.get("jobagent_session", ""), app["session"]):
        raise web.HTTPSeeOther("/login")
    return await handler(request)


async def login(request: web.Request) -> web.Response:
    if request.method == "POST":
        data = await request.post()
        if secrets.compare_digest(str(data.get("token", "")), request.app["token"]):
            response = web.HTTPSeeOther("/dashboard")
            response.set_cookie("jobagent_session", request.app["session"], httponly=True, samesite="Strict", secure=request.secure, max_age=8 * 3600)
            raise response
        return layout("dashboard", '<section class="error">Неверный ключ доступа.</section>')
    return layout("dashboard", '<section><h2>Вход владельца</h2><form method="post" action="/login"><label>Ключ Web GUI <input type="password" name="token" required></label><button>Войти</button></form></section>')


def create_app(bot: Bot, token: str) -> web.Application:
    if len(token) < 24 or not settings.telegram_admin_chat_id.strip():
        raise ValueError("A long WEB_GUI_TOKEN and TELEGRAM_ADMIN_CHAT_ID are required")
    app = web.Application(middlewares=[auth], client_max_size=9 * 1024 * 1024)
    app["bot"] = bot
    app["token"] = token
    app["session"] = secrets.token_urlsafe(32)
    app["csrf"] = secrets.token_urlsafe(32)
    app["scan_state"] = {}
    app["scan_tasks"] = set()
    app["cv_pending"] = {}
    app.router.add_route("*", "/login", login)
    app.router.add_get("/", dispatch)
    app.router.add_get("/{page}", dispatch)
    app.router.add_get("/job/{id:\\d+}", job_detail)
    app.router.add_get("/cv/preview/{token}", cv_preview)
    app.router.add_post("/action/{name}", action)
    app.router.add_get("/application/{id:\\d+}", application_detail)
    app.router.add_get("/application/{id:\\d+}/export", export_application)
    return app


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    token = os.environ.get("WEB_GUI_TOKEN", "")
    if not token:
        raise RuntimeError("WEB_GUI_TOKEN is required")
    if not settings.telegram_bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is required")
    bot = Bot(settings.telegram_bot_token)
    app = create_app(bot, token)

    async def cleanup(_app: web.Application) -> None:
        for task in tuple(_app["scan_tasks"]):
            task.cancel()
        if _app["scan_tasks"]:
            await asyncio.gather(*_app["scan_tasks"], return_exceptions=True)
        await bot.session.close()

    app.on_cleanup.append(cleanup)
    web.run_app(app, host=os.environ.get("WEB_GUI_HOST", "127.0.0.1"), port=int(os.environ.get("WEB_GUI_PORT", "8080")))


if __name__ == "__main__":
    main()
