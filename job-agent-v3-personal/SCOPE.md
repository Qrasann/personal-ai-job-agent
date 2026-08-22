# Personal AI Job Agent — fixed first-release scope

## Goal

A personal AI job-search agent for a user searching from Russia. The user chooses one or more target roles. The agent searches three tracks in parallel:

1. Russia — local Russian vacancies, including remote/hybrid roles.
2. International remote — roles that may be workable from Russia; country and work-authorization restrictions are detected and surfaced.
3. Relocation — foreign roles with relocation, visa-sponsorship or work-permit support signals, plus uncertain opportunities for manual review.

Telegram is the primary control plane.

## Required pipeline

`sources -> normalize -> deduplicate -> match -> choose CV -> Telegram -> apply -> recruiter conversation`

Recruiter conversation is sender-agnostic: a human recruiter and a recruiter AI use the same inbound-message pipeline. The agent must not invent candidate facts and must escalate salary, interview scheduling, start date, documents, offers and uncertain commitments to the user.

## First priorities

- HeadHunter Russia: discovery, apply and chats.
- Telegram vacancies: forwarded posts and channels available to Bot API.
- International remote: RemoteOK first, then additional permitted adapters.
- Relocation classifier: visa sponsorship, relocation support and work-authorization restrictions.
- Multiple CV variants backed by Candidate Facts.

## Deferred, not deleted

Multi-user/SaaS, billing, freelance marketplaces and local aggregators outside Russia remain extension points, but they are not first-release work.
