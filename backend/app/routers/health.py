from fastapi import APIRouter, Depends
from psycopg_pool import AsyncConnectionPool

from app.database import get_pool

router = APIRouter(tags=["health"])


@router.get("/health")
async def liveness():
    return {"status": "ok"}


@router.get("/health/ready")
async def readiness(pool: AsyncConnectionPool = Depends(get_pool)):
    try:
        async with pool.connection() as conn:
            await conn.execute("SELECT 1")
        return {"status": "ready"}
    except Exception as exc:
        return {"status": "not_ready", "error": str(exc)}
