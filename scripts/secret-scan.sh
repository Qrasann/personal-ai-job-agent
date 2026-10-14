#!/usr/bin/env bash
set -euo pipefail

# Lightweight repository guard for obvious high-risk secrets.
# This is intentionally conservative and is not a replacement for key rotation
# or a dedicated secret-scanning service.
pattern='BEGIN (OPENSSH|RSA|EC|DSA) PRIVATE KEY|ghp_[A-Za-z0-9]+|github_pat_[A-Za-z0-9_]+|sk-[A-Za-z0-9_-]{20,}|[0-9]{8,}:[A-Za-z0-9_-]{30,}'

# Inspect commit content and the worktree before publication. Print paths only,
# never matching lines. Ignore the owner's untracked roadmap reference files.
scan_paths() {
    local label="$1"
    shift
    local matches result
    if matches=$(git grep -IlE "$@" "$pattern" -- . \
        ':(exclude)AI-JOB-AGENT-MERGED-ROADMAP-PROPOSAL.md' \
        ':(exclude)CODEX-MAIN-ROADMAP-SYNC-PROMPT.md' 2>/dev/null); then
        echo "Potential secret material detected in $label (paths only):" >&2
        printf '%s\n' "$matches" >&2
        return 1
    else
        result=$?
        if ((result != 1)); then
            echo "Secret scan could not inspect $label." >&2
            return "$result"
        fi
    fi
}

scan_paths 'staged files' --cached
scan_paths 'tracked and nonignored untracked files' --untracked

mapfile -t revisions < <(git rev-list --all)
if ((${#revisions[@]} > 0)); then
    if matches=$(git grep -IlE "$pattern" "${revisions[@]}" -- 2>/dev/null); then
        echo 'Potential secret material detected in Git history (paths only):' >&2
        printf '%s\n' "$matches" >&2
        exit 1
    else
        result=$?
        if ((result != 1)); then
            echo 'Secret scan could not inspect Git history.' >&2
            exit "$result"
        fi
    fi
fi

echo 'Secret scan passed (staged files, worktree and history).'
