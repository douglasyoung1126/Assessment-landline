from psycopg_pool import AsyncConnectionPool
from app.config import settings

_pool: AsyncConnectionPool | None = None


async def init_pool():
    global _pool
    _pool = AsyncConnectionPool(
        conninfo=settings.database_url,
        min_size=settings.pool_min_size,
        max_size=settings.pool_max_size,
        open=False,
    )
    await _pool.open()


async def close_pool():
    if _pool:
        await _pool.close()


async def get_pool() -> AsyncConnectionPool:
    if _pool is None:
        raise RuntimeError("Connection pool not initialized")
    return _pool
