import json
import socket
import ssl

import httpx
import pytest

from app.sources.diagnostics import classify_source_error, render_source_notice, SourceInvalidResponse
from app.search.source_summary import aggregate_source, scan_outcome, SourceSummaryError, render_source_summary
from app.telegram.handlers import _render_search_profiles


@pytest.mark.parametrize('error,code,stage', [
    (httpx.ConnectTimeout('secret URL'), 'NETWORK_CONNECT_TIMEOUT', 'connection'),
    (httpx.ReadTimeout('secret URL'), 'NETWORK_READ_TIMEOUT', 'read'),
    (httpx.PoolTimeout('secret URL'), 'NETWORK_POOL_TIMEOUT', 'pool'),
    (httpx.ProxyError('secret credentials'), 'NETWORK_PROXY_ERROR', 'proxy'),
    (socket.gaierror(-2, 'secret hostname'), 'DNS_RESOLUTION_FAILED', 'dns'),
    (ssl.SSLCertVerificationError('secret cert'), 'TLS_VALIDATION_FAILED', 'tls'),
    (SourceInvalidResponse('secret body'), 'SOURCE_INVALID_RESPONSE', 'response'),
    (json.JSONDecodeError('secret', 'secret body', 0), 'SOURCE_INVALID_RESPONSE', 'response'),
    (RuntimeError('secret token'), 'SOURCE_PROCESSING_FAILED', 'discovery'),
])
def test_classification_never_uses_exception_payload(error, code, stage):
    item = classify_source_error(error)
    assert (item['code'], item['stage']) == (code, stage)
    assert 'secret' not in str(item)
    assert 'secret' not in render_source_notice(['Relocation-first'], 'Remote OK', item)


@pytest.mark.parametrize('status,code', [(403,'HTTP_403_FORBIDDEN'), (429,'HTTP_429_RATE_LIMITED'), (503,'HTTP_5XX_SERVER_ERROR')])
def test_http_is_not_a_connection_failure(status, code):
    request = httpx.Request('GET', 'https://example.test/?token=secret')
    response = httpx.Response(status, request=request)
    item = classify_source_error(httpx.HTTPStatusError('secret', request=request, response=response))
    assert item['code'] == code
    assert item['stage'] == 'http'
    assert 'secret' not in str(item)


@pytest.mark.parametrize('first,second,status,found,failed', [
    ('failed','success','partial',2,1), ('success','failed','partial',2,1),
    ('failed','failed','failed',0,2), ('success','success','success',4,0),
])
def test_independent_attempts_keep_counts_and_failure_history(first,second,status,found,failed):
    sources = {}
    for profile, attempt_status in enumerate([first,second]):
        info = {'status':attempt_status, 'profile_id':profile, 'found':2 if attempt_status=='success' else 0,
                'processed':1 if attempt_status=='success' else 0,
                'diagnostics':[classify_source_error(httpx.ConnectTimeout('secret'))] if attempt_status=='failed' else []}
        aggregate_source(sources,'hh',info)
    info = sources['hh']
    assert (info['status'],info['found'],info['failed']) == (status,found,failed)
    assert len(info['history']) == 2
    assert len(info['diagnostics']) == failed
    assert scan_outcome({'sources':sources}) == ('completed' if status=='success' else status)


def test_legacy_found_defect_reproduced_and_fixed():
    sources = {'hh':{'error':'ConnectTimeout','duration_ms':0}}
    legacy = sources['hh'].copy()
    with pytest.raises(KeyError, match='found'):
        legacy['found'] += 2
    aggregate_source(sources,'hh',{'found':2})
    assert sources['hh']['status']=='partial'
    assert sources['hh']['found']==2
    assert sources['hh']['diagnostics'][0]['code']=='NETWORK_CONNECT_TIMEOUT'


def test_success_missing_found_is_explicit_application_contract_error():
    with pytest.raises(SourceSummaryError):
        aggregate_source({}, 'hh', {'status':'success'})
    item=classify_source_error(KeyError('found'),stage='summary')
    assert item['code']=='SOURCE_SUMMARY_MISSING_FIELD'
    assert item['stage']=='summary'


def test_cache_reuse_deduplicates_eures_observation_but_independent_attempt_does_not():
    sources={}
    for observation in ['a','a','b']:
        aggregate_source(sources,'eures',{'found':2,'partial':True,'cache':True,
                         'partial_failures':1,'partial_failure_observations':{observation:1}})
    assert sources['eures']['found']==6
    assert sources['eures']['partial_failures']==2
    assert sources['eures']['cache']
    assert sources['eures']['attempts']==3


def test_legacy_entities_and_payload_never_escape_into_dashboard():
    line=render_source_summary('hh',{'error':'&#x27;found&#x27;'})
    assert 'SOURCE_SUMMARY_MISSING_FIELD' in line
    assert '&#x27;' not in line
    line=render_source_summary('hh',{'error':'https://secret.test/?token=private'})
    assert 'private' not in line
    notice=render_source_notice(['Career-first','Career-first','Relocation-first'],'Remote OK', classify_source_error(httpx.ConnectTimeout('private')))
    assert notice.count('Career-first')==1
    assert 'Причина устанавливается' in notice
    assert '&quot;' not in notice


def test_source_dashboard_shows_stretch_yield_per_source():
    line = render_source_summary("eures", {
        "name": "EURES", "found": 4, "processed": 4,
        "qualified": 1, "stretch": 2, "filtered": 3, "duplicate": 1,
        "scoring_exclusion_reasons": {"technical_gap": 2, "fit_skip": 1},
    })

    assert "Good: 1" in line
    assert "Stretch: 2" in line
    assert "отфильтровано: 3" in line
    assert "дубликатов: 1" in line
    assert "главный дефицит — техническое соответствие: 2" in line
    assert "блокирующее fit-правило: 1" in line


def test_search_profile_summary_separates_settings_and_scoring_causes():
    text = _render_search_profiles({"12": {
        "name": "Relocation-first <DE>", "processed": 4, "qualified": 1,
        "stretch": 1, "filtered": 2, "preference_filtered": 3,
        "preference_exclusion_reasons": {"domestic_onsite": 3},
        "scoring_exclusion_reasons": {"technical_gap": 2},
    }})

    assert "Relocation-first &lt;DE&gt;" in text
    assert "2 ниже scoring" in text
    assert "3 исключено настройками" in text
    assert "локальная onsite-вакансия не является релокацией: 3" in text
    assert "главный дефицит — техническое соответствие: 2" in text

    bounded = _render_search_profiles({str(index): {
        "name": "Relocation <&> " * 10,
        "preference_exclusion_reasons": {"domestic_onsite": 10},
    } for index in range(20)}, limit=300)
    assert len(bounded) <= 300
    assert "&amp;" in bounded or "Остальные профили" in bounded


def test_source_dashboard_reports_publication_date_field_coverage_without_staleness_claim():
    sources = {}
    aggregate_source(sources, "eures", {
        "status": "success", "found": 4,
        "publication_date_provided": 3, "publication_date_missing": 1,
    })

    line = render_source_summary("eures", sources["eures"])
    assert "поле даты публикации заполнено: 3/4" in line
    assert "просроч" not in line


def test_source_dashboard_shows_publication_age_as_observation_not_hiring_status():
    sources = {}
    aggregate_source(sources, "eures", {
        "status": "success", "found": 4,
        "publication_age_0_7d": 1,
        "publication_age_8_30d": 1,
        "publication_age_over_30d": 1,
        "publication_age_unknown": 1,
    })

    line = render_source_summary("eures", sources["eures"])
    assert "Возраст даты: ≤7 дн. 1, 8–30 дн. 1, >30 дн. 1, неизвестен 1" in line
    assert "вакансия закрыта" not in line


def test_dashboard_keeps_preference_exclusions_distinct_from_scoring_and_errors():
    sources = {}
    aggregate_source(sources, "eures", {
        "status": "success", "found": 0, "discovered": 3, "preference_filtered": 3,
        "preference_exclusion_reasons": {
            "required_visa_sponsorship_missing": 2,
            "other_country_disabled": 1,
        },
    })
    zero_yield = render_source_summary("eures", sources["eures"])
    assert "0 вакансий" in zero_yield
    assert "получено до настроек: 3" in zero_yield
    assert "исключено настройками: 3" in zero_yield
    assert "нет обязательного сигнала visa sponsorship: 2" in zero_yield
    assert "страна не входит в выбранную географию: 1" in zero_yield
    aggregate_source(sources, "eures", {
        "status": "success", "found": 2, "discovered": 2, "filtered": 1,
    })
    line = render_source_summary("eures", sources["eures"])
    assert "получено до настроек: 5" in line
    assert "исключено настройками: 3" in line
    assert sources["eures"]["preference_exclusion_reasons"] == {
        "required_visa_sponsorship_missing": 2,
        "other_country_disabled": 1,
    }
    assert "отфильтровано: 1" in line
    assert "ошибка" not in line
    assert "получено до настроек" not in render_source_summary("eures", {"found": 2})


def test_dense_dashboard_is_bounded_without_breaking_html_entities():
    import html
    from app.search.source_summary import render_source_dashboard
    items={f'source_{n}':{'found':3,'partial':True,'name':'<API> & feed',
                       'diagnostics':[{'code':code,'profiles':['Career-first','Relocation-first']} for code in
                       ['NETWORK_CONNECT_TIMEOUT','HTTP_403_FORBIDDEN','HTTP_429_RATE_LIMITED','HTTP_5XX_SERVER_ERROR']]}
           for n in range(13)}
    view=render_source_dashboard(items)
    assert len(view)<=2600
    assert '…' in view
    assert '&amp;lt;' not in view
    decoded=html.unescape(view)
    assert '<API> & feed' in decoded
    assert html.escape(decoded)==view


def test_dashboard_budgets_include_emoji_utf16_units_and_preserve_html():
    import html
    from app.search.source_summary import render_source_dashboard

    profiles = {str(n): {"name": "🚀" * 80 + "<&>", "processed": 3} for n in range(10)}
    sources = {str(n): {
        "name": "Remote API", "found": 3, "partial": True,
        "diagnostics": [{"code": "NETWORK_CONNECT_TIMEOUT", "profiles": ["🚀" * 80 + "<&>"]}],
    } for n in range(20)}
    source_view = render_source_dashboard(sources)
    profile_view = _render_search_profiles(profiles)
    assert len(source_view.encode("utf-16-le")) // 2 <= 2600
    assert len(profile_view.encode("utf-16-le")) // 2 <= 900
    assert "🚀" in source_view and "🚀" in profile_view
    assert html.escape(html.unescape(source_view)) == source_view
    assert html.escape(html.unescape(profile_view)) == profile_view


@pytest.mark.parametrize("limit", [0, 1, 20])
def test_diagnostic_overflow_note_respects_small_budget(limit):
    from app.search.source_summary import render_source_dashboard

    sources = {"remoteok": {"name": "Remote OK", "found": 5}}
    profiles = {"12": {"name": "Relocation-first", "processed": 5}}
    for view in (render_source_dashboard(sources, limit=limit), _render_search_profiles(profiles, limit=limit)):
        assert len(view.encode("utf-16-le")) // 2 <= limit


@pytest.mark.parametrize('source', ['eures','jobbank','himalayas','remotive','greenhouse','lever','smartrecruiters','arbeitnow'])
def test_adapter_contract_failures_are_response_errors_not_internal_errors(source):
    from app.sources.base import SourceContext
    from app.sources.adapters.eures import EuresSource
    from app.sources.adapters.jobbank import JobBankSource
    from app.sources.adapters.himalayas import HimalayasSource
    from app.sources.adapters.remotive import RemotiveSource
    from app.sources.adapters.greenhouse import GreenhouseSource
    from app.sources.adapters.lever import LeverSource
    from app.sources.adapters.smartrecruiters import SmartRecruitersSource
    from app.sources.adapters.arbeitnow import ArbeitnowSource
    ctx=SourceContext(user_id=1)
    parsers={
        'eures':lambda:EuresSource.parse_search({},'DevOps'),
        'jobbank':lambda:JobBankSource.parse_search('<html>unexpected response</html>'),
        'himalayas':lambda:HimalayasSource.parse_payload({},ctx),
        'remotive':lambda:RemotiveSource.parse_payload({},ctx),
        'greenhouse':lambda:GreenhouseSource.parse_payload({},ctx),
        'lever':lambda:LeverSource.parse_payload({},ctx),
        'smartrecruiters':lambda:SmartRecruitersSource.parse_payload({},ctx),
        'arbeitnow':lambda:ArbeitnowSource.parse_payload({},ctx),
    }
    with pytest.raises(SourceInvalidResponse) as failure:
        parsers[source]()
    item=classify_source_error(failure.value)
    assert item['code']=='SOURCE_INVALID_RESPONSE'
    assert item['stage']=='response'
