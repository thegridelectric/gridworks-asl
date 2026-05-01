# sema — Deployment & Operations

This is the operational reference for deploying sema to production.
The load-bearing axiom is at the top — read it before doing anything irreversible.

---

## 0. The init-vs-migrate boundary (load-bearing — read first)

> **`postgres/init-db.sh` is destructive.** It drops every rulebook-managed
> table at the top of `01-drop-and-create-tables.sql`. It is correct for
> localhost (where the database is ephemeral and re-seeded on every
> `effortless build`) and **catastrophic** for prod once real data exists.

The discipline:

| Environment | Schema bootstrap | Subsequent schema changes |
|---|---|---|
| **localhost** (`postgresql://postgres@localhost:5432/sema`) | `init-db.sh` on every `effortless build` | `init-db.sh` again — blows away & re-seeds |
| **prod** (`bases.effortlessapi.com`) | `init-db.sh` **exactly once**, the day the base is created | `postgres/migrations/migrate-prod.sh` — forward-only, idempotent |

Mechanically:
- `effortless build` invokes `./init-db.sh` with no argument, which uses
  the localhost default. There is **no code path** in this repo that
  invokes `init-db.sh` against the prod conn string except for the
  one-time bootstrap documented in §3 below.
- After bootstrap, every rulebook change requires a hand-authored
  forward-only migration in `postgres/migrations/NNNN-description.sql`.
  `migrate-prod.sh` consults `public.schema_migrations` to apply only
  what's new.

---

## 1. Topology

```
                ┌─────────────────────────────────────────────┐
                │  Control Plane workload: sema-explorer      │
                │  ─────────────────────────────────────────  │
                │  uvicorn  (single port, e.g. 8765)          │
                │    /api/*           → FastAPI handlers      │
                │    /api/auth/*      → magic-links proxy     │
                │    /  /assets/* /…  → built Vite SPA        │
                └────────────────┬───────────────────┬────────┘
                                 │                   │
                Bearer JWT       │                   │  REST
                (RS256, signed   │                   │
                 by tenant T)    │                   │
                                 ▼                   ▼
              ┌──────────────────────────┐   ┌─────────────────────────┐
              │ magiclink.effortlessapi  │   │ bases.effortlessapi.com │
              │ — issues JWTs for one    │   │ — Postgres base for     │
              │   tenant (sema)          │   │   sema (one base, one   │
              │                          │   │   admin conn string)    │
              │ POST /api/tenants/T/     │   │                         │
              │      send-code           │   │ auth.trusted_tenants    │
              │ POST /api/tenants/T/     │   │   row (T, public_key)   │
              │      verify-code         │   │ auth.set_jwt / .email() │
              └──────────────────────────┘   │   (installed by bases)  │
                                             └─────────────────────────┘
```

One tenant (`T`) is shared between **localhost Postgres** and the **prod
bases base**. Same `(tenant_id, public_key_pem)` row goes into
`auth.trusted_tenants` on both. JWTs minted at
`/api/tenants/T/verify-code` verify cleanly on either DB. (See the
`magic-links` skill, "Sharing one tenant across multiple databases".)

**Auth scope today: pure entry gate.** Sema has no row-level security.
The FastAPI `current_user` dependency verifies the Bearer JWT in process
and that's it — verified claims never propagate to postgres. If/when
sema adds RLS-protected tables, swap to a per-request connection helper
that calls `SELECT auth.set_jwt(:token)` so `auth.email()` /
`auth.role()` work inside USING/WITH CHECK clauses (those helpers are
installed by bases in prod, and we'd mirror them in a 02b customization
locally).

---

## 2. Files in this repo

| Path | Purpose |
|---|---|
| `Dockerfile` | Multi-stage build: vite SPA + FastAPI runtime image |
| `.dockerignore` | Keep `node_modules/`, `.venv/`, `.logs/`, `__pycache__/` out of context |
| `.cpln/cpln-app-workload.yaml` | Control Plane workload spec (placeholder-templated, sed'd by CI) |
| `.github/workflows/deploy-app.yaml` | Build → push image → apply workload on push to `main` |
| `postgres/01b-customize-schema.sql` | Hand-written: local `auth.trusted_tenants` mirror matching bases' shape exactly (`tenant_id`, `public_key_pem`, `created_at`). Re-applied on every `init-db.sh`. |
| `postgres/migrations/migrate-prod.sh` | Forward-only migration runner. Tracks state in `public.schema_migrations`. |
| `postgres/migrations/0001_initial_baseline.sql` | Marker only — recorded the day prod was bootstrapped |
| `postgres/migrations/NNNN-*.sql` | One file per rulebook change post-bootstrap |
| `app/api/auth.py` | FastAPI: magic-links proxy routes + Bearer-verifying `current_user` dependency (looks up `public_key_pem` in `auth.trusted_tenants`, RS256-verifies in process). No `SET LOCAL` — auth is just a gate. |
| `app/web/src/lib/auth.ts` | Browser: JWT in `localStorage`, `Authorization: Bearer` injected on every `/api/*` fetch |

---

## 3. One-time prod bootstrap (do this exactly once)

**Pre-conditions:**
- A Postgres base has been provisioned on `bases.effortlessapi.com` for
  sema. You have the admin connection string (`BASE_ADMIN_URL`).
- The magic-links tenant has been minted. You have `MAGICLINK_TENANT_ID`
  and `MAGICLINK_PUBLIC_KEY_PEM`.
- The cpln workload `sema-explorer` exists (created by the first deploy).

**Steps (run from project root):**

```bash
# 1. Apply the full schema. This is the ONLY time init-db.sh
#    will ever touch the prod base.
cd postgres
./init-db.sh "$BASE_ADMIN_URL"
cd ..

# 2. Toggle bases' Magic-Links auth schema on (one-time, superuser-only —
#    installs auth.trusted_tenants + auth.set_jwt / auth.email() / etc.).
curl -sS "https://bases.effortlessapi.com/bases/$BASE_ID/auth/toggle-magic-links" \
  -H "Authorization: Bearer $BASES_JWT" \
  -H "Content-Type: application/json" \
  -d '{"enabled":true}'

# 3. Register the magic-links tenant in the prod base via the bases API
#    (the auth.trusted_tenants table is owned by bases' superuser, so we
#    cannot INSERT directly — use the API instead).
curl -sS "https://bases.effortlessapi.com/bases/$BASE_ID/auth/trusted-tenants" \
  -H "Authorization: Bearer $BASES_JWT" \
  -H "Content-Type: application/json" \
  -d "{\"tenant_id\":\"$MAGICLINK_TENANT_ID\",\"public_key_pem\":\"$MAGICLINK_PUBLIC_KEY_PEM\"}"

# 4. Apply the bases two-role privilege template (anon + admin roles).
curl -sS "https://bases.effortlessapi.com/bases/$BASE_ID/auth/apply-privileges-template" \
  -H "Authorization: Bearer $BASES_JWT" \
  -H "Content-Type: application/json" \
  -d '{"force":false,"returnCredentials":true}'

# 5. Record the bootstrap so future migrate-prod.sh runs know where to start.
postgres/migrations/migrate-prod.sh "$BASE_ADMIN_URL"
```

After step 5, **never run `init-db.sh "$BASE_ADMIN_URL"` again.**
From now on, every rulebook change goes through:

```bash
postgres/migrations/migrate-prod.sh "$BASE_ADMIN_URL"
```

---

## 4. The migration loop (post-bootstrap, every rulebook change)

1. Edit `effortless-rulebook/effortless-rulebook.json`.
2. `effortless build` — regenerates `01-drop-and-create-tables.sql`,
   re-seeds localhost. Commit the build output (per CLAUDE.md's
   build-discipline rule).
3. **Author the forward migration.** Diff the new
   `01-drop-and-create-tables.sql` against the previous version (git
   does this for you). Translate the delta into a forward-only
   `ALTER TABLE` / `CREATE TABLE` / etc. script in
   `postgres/migrations/NNNN-short-description.sql`.
4. Test the migration locally:
   ```bash
   # Reset localhost to the *previous* schema, then apply just the new migration.
   git stash; ./postgres/init-db.sh; git stash pop
   postgres/migrations/migrate-prod.sh \
       "postgresql://postgres@localhost:5432/sema_migration_test"
   ```
5. Deploy. The cpln workflow runs `migrate-prod.sh` against
   `BASE_ADMIN_URL` **before** rolling the new image.
6. Commit the migration alongside any app code changes.

---

## 5. Rotating / revoking the magic-links tenant

The tenant lives in two places: magic-links (private key) and
`auth.trusted_tenants` (public key, on each DB that accepts its JWTs).
The bases-shaped table has no `is_active` flag — revocation is just
deletion.

- **Rotate:** mint a new tenant on magic-links, register its row
  alongside the old one for zero-downtime overlap (POST a second row to
  `/bases/{base_id}/auth/trusted-tenants` in prod, INSERT locally),
  point the app's env vars at the new `MAGICLINK_TENANT_ID`, then
  delete the old row once outstanding sessions have rotated.
- **Revoke:** `DELETE FROM auth.trusted_tenants WHERE tenant_id=...` on
  localhost; in prod use the bases API (the table is owned by bases'
  superuser).
