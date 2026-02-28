# Contributing

## Local Setup

```bash
uv sync --extra dev
pre-commit install
```

## Quality Gates

Run before PR:

```bash
uv run ruff check .
uv run ruff format .
uv run mypy src
uv run pytest
```

## Project Layout

- `src/openclaw_assistant/core`: contracts, events, context, pipeline
- `src/openclaw_assistant/adapters`: integrations with third-party libs/services
- `src/openclaw_assistant/plugins`: pipeline stage plugins
- `src/openclaw_assistant/commands`: CLI subcommands
- `tests`: unit + integration

## Adding a Feature

1. Add/extend interface in `core/contracts.py` if needed.
2. Implement adapter in `adapters/*`.
3. Register behavior via plugin in `plugins/*`.
4. Add tests in `tests/unit` and targeted integration coverage.
