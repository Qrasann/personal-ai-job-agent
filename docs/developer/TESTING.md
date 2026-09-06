# Testing and quality

The project uses several complementary quality checks. Line coverage alone is not treated as proof that business logic is correct.

## Test layers

1. Unit and behavioral tests with pytest.
2. PostgreSQL integration tests against an isolated test database.
3. Branch coverage with a CI minimum gate.
4. Mutation testing for critical matching and scoring logic.

## Local test suite

Without PostgreSQL integration tests:

```bash
python -m pytest -q
```

Integration tests are skipped locally when JOB_AGENT_TEST_DATABASE_URL is not configured.

With the isolated PostgreSQL test database:

```bash
JOB_AGENT_TEST_DATABASE_URL=postgresql+asyncpg://jobagent_test:jobagent_test@127.0.0.1:55432/jobagent_test python -m pytest -q
```

In CI, absence of JOB_AGENT_TEST_DATABASE_URL is an error rather than a skip.

## Coverage

GitHub Actions runs pytest with branch coverage:

```bash
python -m pytest -q --cov=app --cov-branch --cov-fail-under=55
```

v3.4.9 quality baseline:

- Full suite: 117 passed.
- Total application coverage: 58%.
- Candidate bootstrap: 100%.
- Database repository: 65%.
- Fact comparison: 97%.
- Technical Score v2: 93%.

The 55% CI gate is intentionally below the current baseline so that it catches meaningful regressions without making small environment-dependent coverage differences block development.

## Mutation testing

Mutation testing is limited to critical deterministic matching logic:

- app/matching/technical_score.py
- app/matching/fact_comparison.py

Run it with:

```bash
mutmut run
mutmut results
```

v3.4.9 mutation baseline:

- 249 generated mutants.
- 240 killed by tests.
- 9 survived mutation execution.
- 0 timeouts.
- 0 mutation errors.
- 0 meaningful survivors after manual classification.

### Equivalent survivors

The nine surviving mutants in the v3.4.9 baseline were reviewed individually and are equivalent or behaviorally redundant for the current contracts.

Examples include:

- changing an upper score clamp from 100 to 101 when the mathematical input cannot exceed 100;
- removing explicit re.UNICODE behavior that is already the default for Python str regular expressions;
- replacing unused or non-matching empty fallback text with XXXX;
- changing a heading remainder that is ignored when the heading did not match.

These survivors are not known production defects. Raw mutation score is about 96.4%, while all reviewed non-equivalent mutations in the selected critical modules are caught by tests.

Mutation testing in v3.4.9 found real missing assertions for:

- an exact zero Technical Score boundary;
- strongest Candidate Fact IDs;
- separator normalization such as Active_Directory;
- exclusion of a non-persisted zero fact ID.

## Test database safety

docker-compose.test.yml uses a separate PostgreSQL database on localhost port 55432 with tmpfs storage. It must never reuse the personal runtime database or its volumes.

Never use docker compose down -v against the personal Job Agent stack.
