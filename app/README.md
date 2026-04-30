# sema Registry Explorer — `app/`

Phase 2 scaffold per [APP_PLAN.md §12](../APP_PLAN.md). Two halves:

| Half | Path | Stack |
|---|---|---|
| API | [api/](api/) | FastAPI + psycopg + Pydantic. Reads `vw_*`, writes base tables, imports [rulebook-emitters/shared/loader.py](../rulebook-emitters/shared/loader.py) for direct rulebook-JSON reads. |
| Web | [web/](web/) | React 18 + TypeScript + Vite. Typed API client generated from FastAPI's OpenAPI schema. |

## Run it

Two terminals — `api` first, then `web`:

```bash
# Terminal 1 — backend
cd app/api
uv venv .venv && source .venv/bin/activate
uv pip install -r requirements.txt
python -m uvicorn api.main:app --host 127.0.0.1 --port 8765 --reload
#                       │
#                       └─ run from app/, not app/api/, so the package import works

# Terminal 2 — frontend
cd app/web
npm install
npm run gen:api   # generate src/api/schema.d.ts from FastAPI's OpenAPI
npm run dev
```

Open <http://localhost:5173/>. Vite proxies `/api/*` to `http://127.0.0.1:8765`, so the browser never has to think about CORS.

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
    └── vite.config.ts       proxies /api → 127.0.0.1:8765
```

Phase 2 ships a competent shell with two real wired routes (Workbench, Owner) and stubs for the rest of the §8 URL contract. Phase 3 builds out the read-only navigation surface against `vw_*`.
