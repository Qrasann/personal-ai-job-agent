#!/usr/bin/env bash
set -euo pipefail

# Lightweight repository guard for obvious high-risk secrets.
# This is intentionally conservative and is not a replacement for key rotation
# or a dedicated secret-scanning service.
pattern='BEGIN (OPENSSH|RSA|EC|DSA) PRIVATE KEY|ghp_[A-Za-z0-9]+|github_pat_[A-Za-z0-9_]+|sk-[A-Za-z0-9_-]{20,}|[0-9]{8,}:[A-Za-z0-9_-]{30,}'

mapfile -t revisions < <(git rev-list --all)

if ((${#revisions[@]} == 0)); then
    echo 'No Git revisions to scan.'
    exit 0
fi

matches=$(git grep -IlE "$pattern" "${revisions[@]}" -- 2>/dev/null || true)

if [[ -n "$matches" ]]; then
    echo 'Potential secret material detected in Git history:' >&2
    printf '%s\n' "$matches" >&2
    exit 1
fi

echo 'Secret scan passed.'
