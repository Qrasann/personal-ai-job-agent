# Job Agent v3 architecture

## Core invariant

Sources never score candidates and candidates never know source-specific payloads.

```text
Source adapter
    -> NormalizedJob
    -> canonical Job + JobSourceRef
    -> Match Engine(user/profile/search)
    -> JobMatch
    -> Telegram / API / dashboard
```

## Source adapter contract

Implement `app.sources.base.JobSource`:

```python
class JobSource(ABC):
    source_id: str
    name: str
    capabilities: SourceCapabilities

    async def discover(self, context: SourceContext) -> list[NormalizedJob]: ...
```

Optional capability methods are `apply`, `get_messages`, and `send_message`.

Never expose an Apply button just because a site has an application form. Set `capabilities.apply=True` only when the adapter has a supported automated route.

## Country registry

`data/countries.yaml` describes markets. It is metadata, not a promise that a collector exists.

`SourcePlan.implemented` is what Telegram `/sources` uses to distinguish:

- ✅ tested/included adapter;
- 🧩 registered source awaiting adapter.

## Scaling discovery

v3 includes a 10-minute in-memory discovery cache keyed by source + query set so users with identical searches do not immediately hit the same public endpoint repeatedly.

Production evolution:

```text
Scheduler
 -> group SearchProfiles by source/query signature
 -> enqueue one discovery job
 -> store normalized Jobs
 -> fan out matching to N users
```

That should move to Redis/Celery/RQ/Arq or another queue before large-scale deployment.

## Secret model

Do not store OAuth tokens in ordinary SQL text fields in production.

`source_accounts.credential_ref` should point at one of:

- Docker secret / mounted secret for single-user;
- Vault / cloud secret manager;
- encrypted application secret store.

## LLM boundary

The LLM is not the database of truth.

It receives:

- Candidate Facts;
- selected ResumeProfile metadata;
- vacancy text;
- explicit guardrails.

Deterministic rules own hard exclusions, source capability and high-risk decisions.
