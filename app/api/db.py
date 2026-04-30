from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import Any

from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

DATABASE_URL = os.getenv("SEMA_DATABASE_URL", "postgresql://postgres@localhost:5432/sema")

_pool: AsyncConnectionPool | None = None


async def init_pool() -> AsyncConnectionPool:
    global _pool
    if _pool is None:
        _pool = AsyncConnectionPool(
            conninfo=DATABASE_URL,
            min_size=1,
            max_size=8,
            kwargs={"row_factory": dict_row},
            open=False,
        )
        await _pool.open()
    return _pool


async def close_pool() -> None:
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


@asynccontextmanager
async def conn():
    pool = await init_pool()
    async with pool.connection() as c:
        yield c


async def fetch_all(sql: str, *params: Any) -> list[dict[str, Any]]:
    async with conn() as c:
        async with c.cursor() as cur:
            await cur.execute(sql, params)
            return await cur.fetchall()


async def fetch_one(sql: str, *params: Any) -> dict[str, Any] | None:
    async with conn() as c:
        async with c.cursor() as cur:
            await cur.execute(sql, params)
            return await cur.fetchone()
