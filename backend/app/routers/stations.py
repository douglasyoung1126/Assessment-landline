from fastapi import APIRouter, Depends
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

from app.database import get_pool

router = APIRouter(tags=["stations"])


@router.get("/stations")
async def list_stations(pool: AsyncConnectionPool = Depends(get_pool)):
    async with pool.connection() as conn:
        conn.row_factory = dict_row
        cur = await conn.execute(
            "SELECT id, code, name, city, state FROM stations ORDER BY city"
        )
        return await cur.fetchall()
