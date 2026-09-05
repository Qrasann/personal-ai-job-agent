from app.matching.fact_comparison import extract_requirement_importance


def test_synergy_real_headings_classify_preferred_and_neutral_sections():
    text = """В ПРОЦЕССЕ РАБОТЫ НЕОБХОДИМО
Jitsi
Kubernetes
ЧТО БУДЕТ ВАШИМ ПРЕИМУЩЕСТВОМ
Linux
Docker
Ansible
Плюсом будет:
Nginx
Prometheus
Grafana
ДЛЯ ВАС МЫ ПРЕДЛАГАЕМ
PostgreSQL
"""

    importance = extract_requirement_importance(text)

    assert importance["Jitsi"] == "unknown"
    assert importance["Kubernetes"] == "unknown"

    assert importance["Linux"] == "preferred"
    assert importance["Docker"] == "preferred"
    assert importance["Ansible"] == "preferred"
    assert importance["Nginx"] == "preferred"
    assert importance["Prometheus"] == "preferred"
    assert importance["Grafana"] == "preferred"

    assert importance["PostgreSQL"] == "unknown"
