# Personal AI Job Agent v3.1

Personal job-search agent with Telegram as the main interface. The first production target is one user searching **from Russia** in three parallel tracks:

- 🇷🇺 Russian vacancies;
- 🌍 international remote;
- ✈️ relocation / visa-sponsorship opportunities.

The role is configurable from Telegram, so the same agent can search DevOps today and another selected position later without rewriting code.

## Core pipeline

```text
HH Russia / remote sources / Telegram posts / future ATS adapters
                         ↓
                    NormalizedJob
                         ↓
              dedupe + eligibility signals
                         ↓
              Candidate Facts + matcher
                         ↓
                 best CV selection
                         ↓
                     Telegram
                         ↓
              apply / open source / skip
                         ↓
               recruiter conversation
                 human OR recruiter AI
```

## Telegram commands

```text
/start
/status
/settings

/role DevOps Engineer
/roleadd Infrastructure Engineer
/roles

/mode
/mode local on|off
/mode remote on|off
/mode relocation on|off

/scan
/jobs
/sources

/facts
/fact add <text>
/fact commercial <id>
/fact noncommercial <id>

/resumes
/resumeadd name|language|role
/resumebindhh <resume_id> <hh_resume_id>

/chats
/pause
/resume
```

A forwarded Telegram vacancy is parsed and sent through the same matcher. Posts from channels where the bot receives `channel_post` updates are also ingested.

## Default search modes

```yaml
modes:
  local_ru: true
  remote_international: true
  relocation: true
```

The international scorer treats `Remote worldwide` as strong evidence, region-only remote such as EMEA as uncertain, and explicit US/EU-only/work-authorization restrictions as a major negative. Relocation and visa-support wording is analyzed separately.

## Candidate Facts

Candidate Facts are the source of truth. CVs and recruiter replies may only use facts stored there. A fact marked `commercial=false` must never be presented as commercial/production experience.

Recommended initial CV set:

- DevOps RU — HH/Russia;
- DevOps EN — remote/relocation;
- Linux/Infrastructure RU;
- later: Infrastructure EN.

## Recruiter and recruiter-AI conversations

HH inbound chat messages go through one response pipeline regardless of whether the sender is a human recruiter or an automated recruiter. The LLM generates a factual draft and confidence score. Sensitive or uncertain decisions require Telegram confirmation.

Default safety:

```env
AUTO_APPLY=false
AUTO_REPLY=false
```

Keep both disabled until several manual end-to-end runs have been reviewed.

## First launch

```bash
cp .env.example .env
nano .env
docker compose up -d --build
docker compose logs -f app
```

Fill at least:

```env
TELEGRAM_BOT_TOKEN=
TELEGRAM_ADMIN_CHAT_ID=
HH_ACCESS_TOKEN=
HH_RESUME_ID=
HH_USER_AGENT=PersonalJobAgent/0.1 (your-email@example.com)
OPENAI_API_KEY=
```

Then in Telegram:

```text
/start
/settings
/role DevOps Engineer
/scan
```

See `SCOPE.md` and `ROADMAP.md`.
