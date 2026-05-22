# sema Registry Explorer — `app/`

Phase 2 scaffold per [APP_PLAN.md §12](../APP_PLAN.md). Two halves:

| Half | Path | Stack |
|---|---|---|
| API | [api/](api/) | FastAPI + psycopg + Pydantic. Reads `vw_*`, writes base tables, imports [rulebook-emitters/shared/loader.py](../rulebook-emitters/shared/loader.py) for direct rulebook-JSON reads. |
| Web | [web/](web/) | React 18 + TypeScript + Vite. Typed API client generated from FastAPI's OpenAPI schema. |

## First-time setup

On a fresh checkout, **neither half has its dependencies installed** — `app/api/.venv`
and `app/web/node_modules` don't exist yet, so `./start.sh` will fail with
`api/.venv/bin/activate: No such file or directory` and `sh: vite: command not found`.
Install both halves once:

```bash
# Backend deps (creates app/api/.venv)
cd app/api
uv venv .venv && source .venv/bin/activate
uv pip install -r requirements.txt

# Frontend deps (creates app/web/node_modules)
cd ../web
npm install
```

Prerequisites on your PATH: `uv`, `node`/`npm` (Node 20+), `psql`, and a running
**Docker** (Docker Desktop or equivalent) — the database runs in a Docker container,
see [Setting up Postgres](#setting-up-postgres-docker) below.

You also need a running, initialized `sema` database, or every `vw_*`-backed route
returns nothing and `/api/health` reports `"db": false`. See the WIP section below.

## Run it

Two terminals — `api` first, then `web`:

```bash
# Terminal 1 — backend
cd app/api
source .venv/bin/activate
python -m uvicorn api.main:app --host 127.0.0.1 --port 8765 --reload
#                       │
#                       └─ run from app/, not app/api/, so the package import works

# Terminal 2 — frontend
cd app/web
npm run gen:api   # generate src/api/schema.d.ts from FastAPI's OpenAPI (API must be up)
npm run dev
```

Open <http://localhost:8766/>. Vite proxies `/api/*` to `http://127.0.0.1:8765`, so the browser never has to think about CORS.

> Or, from the project root, `./start.sh` nukes whatever's on `:8765` / `:8766` and restarts both halves from scratch (logs land in `.logs/`). It does **not** install dependencies — run the first-time setup above before the first `./start.sh`.

## Setting up Postgres (Docker)

> **Prerequisite: Docker must be installed and running** (Docker Desktop or
> equivalent). `start-db.sh` aborts with a clear message if `docker info` fails.
>
> **Status: WIP.** The Docker path below is **verified working** (`/api/health`
> reports `"db": true` after it). The "open questions" at the end are not yet
> resolved — refine as you go.

The API connects with `SEMA_DATABASE_URL`. Two things must exist for it to resolve:
a **`postgres` role** and a **`sema` database**. The official `postgres` Docker image
gives you both for free, which avoids the `FATAL: role "postgres" does not exist`
error you hit against a native Homebrew cluster (whose superuser is named after your
macOS user, not `postgres`).

### Easy path: `./start-db.sh`

From the project root:

```bash
./start-db.sh        # create/start the sema-pg container on :5433, init schema if empty
```

That script is **idempotent** — re-running it starts the existing container and skips
the schema build if it's already there. Flags: `--no-init` (container only),
`--reinit` (rebuild schema unconditionally). It runs `postgres/init-db.sh` for you.

The container listens on **host port 5433** (not 5432) to coexist with any native
Homebrew Postgres already holding 5432. Accordingly, `app/api/.env` sets:

```
SEMA_DATABASE_URL=postgresql://postgres@localhost:5433/sema
```

> ⚠️ The `.env.example` ships with port **5432** and a **relative** `SEMA_RULEBOOK_PATH`.
> When uvicorn runs from `app/` (as `./start.sh` does), that relative path doesn't
> resolve — set `SEMA_RULEBOOK_PATH` to an **absolute** path in your `.env`.

### What `start-db.sh` runs under the hood

```bash
docker run -d --name sema-pg \
  -e POSTGRES_DB=sema \
  -e POSTGRES_HOST_AUTH_METHOD=trust \   # app connects as postgres with no password
  -p 5433:5432 \
  postgres:16
# then, once pg_isready passes:
cd postgres && ./init-db.sh "postgresql://postgres@localhost:5433/sema"
```

After that, `curl http://127.0.0.1:8765/api/health` reports `"db": true` (restart the
API if it was started before the DB came up — the connection pool caches the failure).

**Open questions / not yet checked:**

- The `.secrets/sema-tenant.json` localhost re-seed step in `init-db.sh` (needs `jq`);
  login-related, skipped silently when the file is absent — fine for read-only Explorer
  use, untested for the auth flow.
- Post-`effortless build` fix scripts (`scripts/fix_lookup_functions.py`,
  `scripts/fix_aggregations.py`) — see the build-discipline note below; confirm whether
  they're needed on a *first* init or only after a rebuild.
- Data persistence: the container has no named volume, so `docker rm sema-pg` discards
  the DB (just re-run `./start-db.sh` to rebuild). Add a `-v` mount if you want it to
  survive container removal.

Useful URLs while the backend is up:

- <http://127.0.0.1:8765/docs> — Swagger UI
- <http://127.0.0.1:8765/api/health> — health check + rulebook table summary
- <http://127.0.0.1:8765/openapi.json> — raw OpenAPI schema (the source for `gen:api`)

## Regenerating the typed client

The TypeScript client is generated from the live FastAPI server. **Whenever the API changes**, regenerate:

```bash
cd app/web
npm run gen:api
```

Output lands in [`web/src/api/schema.d.ts`](web/src/api/schema.d.ts) — committed, so reviews can see the wire shape change.

## Database connection

`api/db.py` reads `SEMA_DATABASE_URL` (default `postgresql://postgres@localhost:5432/sema`). Override via `app/api/.env` (copy from `.env.example`).

## Build-discipline reminder (load-bearing)

⚠️ **After every `effortless build`** the rulebook-to-postgres transpiler regenerates broken lookup and aggregation functions ([APP_PLAN-NOTES.md §2](../APP_PLAN-NOTES.md#2-theres-a-transpiler-bug-landmine-tooling-defuses-it-dont-let-a-build-silently-re-arm-it)). Always run the override scripts before restarting the backend:

```bash
effortless build
python3 scripts/fix_lookup_functions.py
python3 scripts/fix_aggregations.py
cd postgres && ./init-db.sh
```

**Canary symptom** that the workaround didn't run: `SELECT name, draft_type_version_count FROM vw_owners;` returns `1` for every owner. If you see that, don't chase it as a FastAPI bug — re-run the scripts.

## Layout

```
app/
├── api/
│   ├── main.py              FastAPI app, CORS, router mount, /health
│   ├── db.py                psycopg async connection pool
│   ├── loader.py            shim over rulebook-emitters/shared/loader.py
│   ├── models.py            Pydantic response models for vw_* surface
│   ├── routes/
│   │   ├── owners.py        /api/owners
│   │   ├── types.py         /api/types, /api/type-versions/{type}/{version}/...
│   │   ├── enums.py         /api/enums, /api/enum-versions/{enum}/{version}/...
│   │   ├── formats.py       /api/formats
│   │   ├── helpers.py       /api/helpers
│   │   ├── projections.py   /api/projections
│   │   ├── upgrades.py      /api/type-upgrades, /api/enum-upgrades
│   │   └── search.py        /api/search
│   ├── requirements.txt
│   └── .env.example
└── web/
    ├── src/
    │   ├── main.tsx         React entry
    │   ├── router.tsx       React Router skeleton matching APP_PLAN §8
    │   ├── styles.css       three-pane shell + status pill styles
    │   ├── api/
    │   │   ├── client.ts    typed openapi-fetch client
    │   │   └── schema.d.ts  generated from FastAPI's OpenAPI (commit this)
    │   ├── components/
    │   │   ├── ThreePaneShell.tsx
    │   │   ├── StatusPill.tsx          draft / active / deprecated / retired
    │   │   └── Placeholder.tsx         stub renderer for routes that land later
    │   └── routes/
    │       ├── Workbench.tsx           §7 — wired to /api/owners + /api/health
    │       └── Owner.tsx               /v/{owner} — wired to /api/owners/{name}
    ├── package.json
    ├── tsconfig.json
    └── vite.config.ts       listens on :8766, proxies /api → 127.0.0.1:8765
```

Phase 2 ships a competent shell with two real wired routes (Workbench, Owner) and stubs for the rest of the §8 URL contract. Phase 3 builds out the read-only navigation surface against `vw_*`.
