# Architecture — Personal AI Job Agent v3.3.3

```text
Sources
  ├─ HH public discovery (RU)
  ├─ RemoteOK
  ├─ Telegram posts/forwards
  └─ future ATS/local boards
          ↓
    Source adapters
          ↓
    NormalizedJob
          ↓
      Deduplication
          ↓
     Matching engine
    ┌─────┼────────┐
    │     │        │
 Russia Remote Relocation
    └─────┼────────┘
          ↓
 Candidate Facts + CV selector
          ↓
       Telegram
          ↓
  prepare/apply/manual decision
```

## HH boundary

HH is discovery-only in the default build. The adapter deliberately does not fan out into one details request per result, because anonymous HH API traffic may be challenged with CAPTCHA. Private applicant methods are dormant unless explicitly enabled with legitimate existing credentials.

## Safety boundary

The system does not bypass CAPTCHA or anti-bot protections. A source failure is isolated: one source can stop while the remaining collectors keep running.
