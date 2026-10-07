# `check` and `test` are two distinct gates, mirroring the CI jobs of the same name.

default:
    @just --list

# Lint, format and typing — same as the CI `check` job
check:
    uv run ruff format --check src tests
    uv run ruff check src tests
    uv run mypy src tests

# Unit tests with coverage — same as the CI `test` job
test pytest_args="":
    uv run -- pytest --cov=gnome_extensions_cli --cov-report=term-missing {{pytest_args}}

# Known vulnerabilities in the installed dependencies (from uv.lock)
audit:
    uv run --no-sync -- pip-audit

# Outdated direct dependencies + GitHub actions update (pinned by SHA)
outdated:
    uv tree --outdated --depth 1
    GITHUB_TOKEN=$(gh auth token) uvx gha-update

# Format and apply auto-fixable lint rules
format:
    uv run ruff format src tests
    uv run ruff check --fix src tests

# Bump the version, commit and tag; the CI publishes on the tag
release bump="patch":
    echo "{{bump}}" | grep -E "^(major|minor|patch)$"
    uv version --bump "{{bump}}"
    git add pyproject.toml uv.lock
    git commit --message "🔖 New release: `uv version --short`"
    git tag "`uv version --short`"

[confirm('Confirm push --tags ?')]
publish:
    git log -1 --pretty="%B" | grep '^🔖 New release: '
    git push
    git push --tags
