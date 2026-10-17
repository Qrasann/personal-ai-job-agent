import subprocess
from pathlib import Path

import pytest


SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'secret-scan.sh'


def git(root, *args):
    return subprocess.run(['git', *args], cwd=root, check=True, capture_output=True, text=True)


@pytest.fixture
def repository(tmp_path):
    git(tmp_path, 'init', '--quiet')
    (tmp_path / 'safe.txt').write_text('safe baseline\n')
    git(tmp_path, 'add', 'safe.txt')
    git(tmp_path, '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '--quiet', '-m', 'baseline')
    return tmp_path


def scan(root):
    return subprocess.run(['bash', str(SCRIPT)], cwd=root, capture_output=True, text=True)


@pytest.mark.parametrize('location', ['untracked', 'tracked', 'staged'])
def test_secret_guard_checks_uncommitted_content_without_printing_secret(repository, location):
    token = 'ghp_' + 'SyntheticGuardFixture123'
    target = repository / 'candidate.txt'
    if location == 'tracked':
        target.write_text('safe\n')
        git(repository, 'add', target.name)
        git(repository, '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '--quiet', '-m', 'safe')
    target.write_text(token)
    if location == 'staged':
        git(repository, 'add', target.name)
        target.write_text('safe working copy after staging\n')
    result=scan(repository)
    assert result.returncode==1
    assert target.name in result.stderr
    assert token not in result.stdout+result.stderr


def test_secret_guard_accepts_clean_repository_and_ignores_local_credentials(repository):
    (repository / '.gitignore').write_text('.env\n')
    (repository / '.env').write_text('ghp_' + 'SyntheticIgnoredFixture')
    result=scan(repository)
    assert result.returncode==0
    assert 'staged files, worktree and history' in result.stdout


def test_secret_guard_still_rejects_secret_in_history(repository):
    token='ghp_' + 'SyntheticHistoricalFixture'
    target=repository / 'candidate.txt'
    target.write_text(token)
    git(repository,'add',target.name)
    git(repository,'-c','user.name=Test','-c','user.email=test@example.invalid','commit','--quiet','-m','fixture')
    target.write_text('safe current copy\n')
    git(repository,'add',target.name)
    result=scan(repository)
    assert result.returncode==1
    assert 'Git history' in result.stderr
    assert token not in result.stdout+result.stderr
