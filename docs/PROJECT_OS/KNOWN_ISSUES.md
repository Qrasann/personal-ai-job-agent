# Known Issues

## Resolved in the current development branch
- Concurrent scheduled/manual scans could both observe a missing JobMatch and then race to insert the same `(job_id, profile_id, search_profile_id)`. `save_match` now uses an atomic PostgreSQL upsert and the fix passed a local scheduled/manual scan smoke test.
- Relocation discovery initially used `relocation_queries` while matching scored only career `queries`, filtering otherwise relevant broad-role results. Matching now uses the active strategy's discovery queries.
- Generic description text could be misread as a salary for non-HH sources. Notifications and details now use only structured salary values or explicit source salary/card text.

- EURES response bodies failed with a TLS record-layer error when the client
  negotiated compressed encoding. In a live container check, the default
  compressed request reproduced the failure, while `Accept-Encoding: identity`
  returned a full 50-result JSON response. The first complete post-update
  dual-profile scan returned EURES search and detail responses without SSL
  errors, and `scan_all` completed. The underlying network/server cause is not
  established; monitor later scheduled runs.

- work_permit, relocation_package and immigration_support are not separate Job columns yet; v3.5.2 infers them conservatively from vacancy text.
- Source/country priority affects processing order, not Recommendation Model v2 score yet.
- City priority exists in the preference engine but dedicated Telegram city-priority buttons are pending.
- Country picker is limited to data/countries.yaml.
- Only implemented adapters actually scan; future registered sources still need collectors.
- HH is primarily domestic and RemoteOK is tech-heavy. Arbeitnow adds Germany coverage but its current feed can legitimately contain no low-barrier role matches; additional legal-work/visa-capable country sources are still needed.
- Georgia adapters enter a profile's scan only when `GE` is selected. The owner
  confirmed a Relocation-first GE scan on 2026-10-11: EURES returned 16
  vacancies, HR.ge returned 2, JOBS.GE returned HTTP 410, and Arbeitnow had a
  transient `ReadTimeout`. JOBS.GE is paused in the source plan; HR.ge remains
  enabled while recurring reuse permission is unverified. The deployed
  follow-up adds one bounded retry for Arbeitnow transport failures. A later
  Telegram scan log confirmed a timeout recovered on retry with HTTP 200. The
  owner confirmed `/sources` displays JOBS.GE as paused and provided a completed
  `/scanstatus` report.
- On the v3.5.7 candidate, Armenia (`AM`) is selectable and Lineate's public
  Greenhouse board is connected for selected AM/GE markets. Its current
  DevOps/Infrastructure match is for a Georgian office; the Yerevan postings
  on that board are data-engineering roles and do not match current queries.
  The candidate is deployed to local Compose for owner acceptance, while
  `main` and the formal release remain v3.5.6. Its startup scan did not show a
  Greenhouse request; verify the effective market/source settings with
  `/sources` and a targeted Telegram `/scan`. The official e-work/workforall
  access contract remains unverified. Staff.am
  prohibits automated scraping without permission, and Job.am restricts
  unauthorized reuse and redistribution.
- The official Armenian `workpermit.am` portal describes employer-side
  foreign-hiring and work-residence processing, and states that EAEU citizens
  working in Armenia are exempt from work-permit documents. Its public UI has
  a job-finding FAQ, but the answer and anonymous job-discovery/feed access are
  unverified. Candidate nationality must not be inferred from profile country.
- Georgia's Labour Migration Law changes effective 2026-03-01 require covered
  foreign workers in local paid employment to obtain a right to work through
  the employer and follow the applicable immigration procedure. Search target
  `GE` does not establish individual work eligibility.
- `/salary minimum` currently affects scoring when a structured salary exists;
  it does not hard-filter. The Telegram text says “minimum for filter.” In the
  owner-provided `/job 580`, 90,000 RUB appeared in the description while
  structured salary stayed unknown, so the value was not used for scoring.
- Job Bank Canada adds international TFW coverage, but an LMIA request or
  permission to apply does not establish sponsorship or candidate eligibility.
  Initial coverage is one page, six queries and twelve details per profile;
  the five-second request pacing adds up to about 90 seconds plus network time.
  Decimal CAD/hour salaries are preserved as source text; structured salary
  normalization and display are pending. A Telegram update took 162.7 seconds
  with twelve Job Bank detail calls visible; `/scanstatus` measured Job Bank at
  99.5 seconds. Preserve the five-second request interval while evaluating a
  safe pacing improvement; do not increase request volume or parallelize calls.
- Full CI is required before merge; live Telegram polling and dual-profile scan smoke tests passed on the local deployment.
