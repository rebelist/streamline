# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Streamline is an engineering metrics platform. It ingests data from Jira (GitLab/AWS/Datadog are planned), stores it in MongoDB, computes workflow/flow metrics (cycle time, lead time, throughput, velocity, sprint cycle time), and exposes them over a FastAPI HTTP API that Grafana renders via the Infinity datasource.

Python 3.14, managed with `uv`. Runtime services (MongoDB, Grafana, the API) run in Docker.

## Commands

```bash
make init          # Copy .env.example/settings.ini.example into place (first-time setup)
make dev           # Start docker deps + `uv sync` + `fastapi dev` for local API hot-reload
make build         # Build the API Docker image (prod profile)
make start         # Run full stack via docker (prod), create DB indexes, open Grafana
make shutdown      # Stop the prod stack

make tests         # uv run pytest, fail-fast, failed-first
make coverage      # pytest with HTML coverage report -> var/coverage
make check         # Run all pre-commit hooks (ruff, ruff-format, pyright, ...)
make check ruff    # Run a single pre-commit hook by name
```

Direct tooling (what the make targets wrap):

```bash
uv run pytest                                  # all tests
uv run pytest tests/path/to/test_x.py          # single file
uv run pytest tests/path/to/test_x.py::TestClass::test_method   # single test
uv run pytest -m unit                          # by marker: unit | integration | e2e
uv run pyright                                 # strict type check (src + tests)
uv run ruff check --fix && uv run ruff format  # lint + format
```

CLI commands (data ingestion / DB maintenance) run inside the API container via `bin/console`, which is just `docker-compose exec api uv run streamline <command>`:

```bash
bin/console database:synchronize   # Fetch sprints + tickets from Jira into MongoDB
bin/console database:index         # Create MongoDB indexes
bin/console database:clear         # Empty all collections
```

The `streamline` entry point itself is defined in `pyproject.toml` (`[project.scripts]`) and is the rich-click group in `handlers/cli/console.py`.

## Architecture

The code under `src/rebelist/streamline/` follows a layered / hexagonal (ports-and-adapters) structure. Dependencies point inward: handlers → application → domain, with infrastructure implementing the protocols the inner layers depend on. Everything is wired together in one place.

- **`domain/`** — Pure business logic, no I/O. Metric calculators (`domain/metrics/flow/calculators.py`: cycle/lead time, throughput, velocity), the working-time engine (`domain/time/calculator.py`, which counts only working days/hours per `WorkCalendarProtocol`), and the aggregate models + repository **protocols** for `sprint` and `ticket`. The concrete repositories live in infrastructure.

- **`application/`** — Orchestration. Split into two sub-domains:
  - `compute/` — read side. Use cases (`compute/use_cases/flow.py`) pull data through repositories and run domain calculators; `FlowMetricsService` (`compute/services.py`) is the single façade the API calls.
  - `ingestion/` — write side. `jobs/workflow.py` defines `SprintJob` and `TicketJob` (both `Executable`) that pull from Jira and persist via document repositories. Jobs track **incremental sync state** in a `Job` record (`sprint_offset`, `tickets_done_at`) so each run resumes where the last left off.

- **`infrastructure/`** — Adapters to the outside world: `jira/gateway.py` (Jira client wrapper with tenacity retries), `mongo/` repositories, `datetime/normalizer.py` (timezone normalization), `monitoring/logger.py` (loguru). Note **two repository flavors per aggregate**: a read repository (e.g. `MongoSprintRepository`, returns domain models) and a document repository (e.g. `MongoSprintDocumentRepository`, used by ingestion to write raw docs).

- **`handlers/`** — Entry points (the "driving" adapters):
  - `api/` — FastAPI app (`api/main.py`) + routers under `api/metrics/`. Endpoints are mounted at `/v1/metrics/flow/*`, return the generic `MetricResponse[DataPoint, Meta]` envelope, and resolve dependencies via `dependency_injector`'s `@inject` + `Provide[Container.x]`.
  - `cli/` — rich-click commands under `cli/commands/`, registered in `cli/console.py`. Commands receive the container via the click `Context`.

- **`config/`** — The composition root.
  - `container.py` — a `dependency_injector` `DeclarativeContainer`. **All wiring happens here.** Services are `Singleton`s; private ones are name-mangled (`__jira_gateway`, etc.); public providers are what handlers reference. `Container.create()` loads `.env` values. `auto_wire` is configured for the `handlers.api` package. When adding a service, register it here and inject it — do not instantiate dependencies directly.
  - `settings.py` — Pydantic `Settings` (frozen) loaded from `settings.ini` (`[app]`, `[workflow]`, `[jira]` sections). Secrets/connection strings come from `.env`; behavioral config comes from `settings.ini`.

### Data flow

1. `database:synchronize` → `SprintJob`/`TicketJob` → `JiraGateway` fetches → Mongo document repositories persist; `JobRepository` records sync watermark.
2. Grafana → `GET /v1/metrics/flow/*` → router → `FlowMetricsService` → use case → read repository + domain calculator → `MetricResponse`.

## Conventions

- **Strict pyright** (`typeCheckingMode = "strict"`) and **ruff** with Google-style docstrings, single quotes, 120-col lines. Docstrings are required on public modules/classes/methods (enforced by ruff `D`). pre-commit runs all of this.
- Tests live under `tests/` mirroring the `src/` package tree; classes are `Test*`, functions `test_*`. Use the `unit`/`integration`/`e2e` markers (strict markers are enabled).
- Metric calculations are based on **working days/hours**, not calendar time, and are timezone-sensitive — see the README's "Notes" and "Caveats" sections before changing time logic.
