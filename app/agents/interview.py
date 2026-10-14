from __future__ import annotations

from app.matching.fact_comparison import FactComparison


_EXERCISES: dict[str, tuple[str, str, tuple[str, ...]]] = {
    "Linux": (
        "A Linux service is responding slowly and CPU usage is near 100%. How do you diagnose it without rebooting?",
        "Walk through the first five minutes of investigation and explain what evidence each command provides.",
        ("Check load and per-process CPU", "Inspect service logs and recent changes", "Choose a safe mitigation and verify recovery"),
    ),
    "Docker": (
        "An application container cannot resolve its database service, although both containers are running.",
        "Explain how you would inspect Compose networks, DNS names, health checks and connection configuration.",
        ("Test name resolution from inside the app container", "Check shared network membership and service name", "Separate startup ordering from readiness"),
    ),
    "Docker Compose": (
        "A Compose deployment starts, but one service repeatedly exits and its dependent service fails health checks.",
        "Describe a safe diagnosis and recovery plan without deleting persistent data.",
        ("Read service logs and exit status", "Inspect health-check and dependency definitions", "Preserve volumes and verify rollback"),
    ),
    "Nginx": (
        "Users receive HTTP 502 from Nginx after an application release.",
        "Trace the request from listener to upstream and show how you would isolate the failing hop.",
        ("Inspect error/access logs", "Verify upstream address, port and protocol", "Test config before reload and verify recovery"),
    ),
    "Kubernetes": (
        "A Deployment rollout is stuck and new Pods enter CrashLoopBackOff.",
        "Explain which objects and events you would inspect, and how you would roll back safely.",
        ("Inspect rollout status, Pod events and previous container logs", "Check probes, config and resource limits", "Use a controlled rollback and verify readiness"),
    ),
    "Networking": (
        "A service intermittently fails to reach another host by name but works by IP.",
        "Build a diagnostic path from DNS resolution through routing and the application port.",
        ("Compare resolver answers and TTL", "Check routes and firewall path", "Test the target port and correlate timestamps"),
    ),
    "DNS": (
        "A service intermittently resolves a hostname to an unexpected address after a deployment.",
        "Trace the answer from the client resolver to the authoritative record and explain how you would verify cache and TTL effects.",
        ("Compare answers from the host and a trusted resolver", "Inspect record type, TTL and recent changes", "Avoid changing records until the affected cache and rollback path are known"),
    ),
    "TLS": (
        "Clients report TLS handshake failures after a certificate renewal.",
        "Check hostname, certificate chain, expiry, SNI and listener configuration before making changes.",
        ("Inspect the presented chain and SAN", "Check SNI and configured certificate path", "Validate configuration before reload and verify a client handshake"),
    ),
    "Security Operations": (
        "A server may have a compromised account, but the scope is not yet known.",
        "Describe a proportionate containment and evidence-preservation plan, including who you would notify.",
        ("Follow the incident response owner and access controls", "Preserve logs and record a timeline before cleanup", "Contain narrowly, rotate affected credentials and verify recovery"),
    ),
    "PostgreSQL": (
        "A production query became slow while database CPU and connection counts increased.",
        "Explain how you would distinguish a bad plan, lock contention and connection pressure.",
        ("Inspect query plan and duration", "Check locks and active sessions", "Propose a reversible change and measure it"),
    ),
    "CI/CD": (
        "A deployment pipeline fails after a dependency update, but the test job passed.",
        "Trace artifacts and environment differences, then describe a safe rollback or retry.",
        ("Find the first failing stage and exact artifact", "Compare build/test/deploy environments", "Avoid rerunning a non-idempotent deploy blindly"),
    ),
    "Prometheus": (
        "An availability alert is firing, but users report the service is healthy.",
        "Review the signal, labels, evaluation window and alert routing before changing thresholds.",
        ("Validate the underlying time series", "Check scrape gaps and alert expression", "Avoid hiding a real outage with a wider threshold"),
    ),
}

_IMPORTANCE_ORDER = {"required": 0, "preferred": 1, "unknown": 2}


def build_interview_plan(comparison: FactComparison, *, limit: int = 5) -> tuple[dict, ...]:
    """Build short vacancy-specific practice exercises without an LLM call."""
    items = sorted(
        comparison.requirements,
        key=lambda item: (_IMPORTANCE_ORDER.get(item.importance, 3), item.skill.casefold()),
    )
    plan: list[dict] = []
    for item in items:
        exercise = _EXERCISES.get(item.skill)
        if not exercise:
            continue
        scenario, task, criteria = exercise
        plan.append({
            "skill": item.skill,
            "importance": item.importance,
            "candidate_status": item.status,
            "scenario": scenario,
            "task": task,
            "criteria": criteria,
        })
        if len(plan) >= max(1, min(limit, 8)):
            break
    return tuple(plan)
