from fastapi import APIRouter, Depends, Query
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

from app.database import get_pool

router = APIRouter(tags=["trips"])


@router.get("/trips/search")
async def search_trips(
    origin: str = Query(..., description="Origin station code"),
    destination: str = Query(..., description="Destination station code"),
    date: str = Query(..., description="Travel date YYYY-MM-DD"),
    pool: AsyncConnectionPool = Depends(get_pool),
):
    async with pool.connection() as conn:
        conn.row_factory = dict_row
        cur = await conn.execute(
            """
            SELECT
                t.id,
                t.date::text,
                s.departure_time::text  AS departure_time,
                s.arrival_time::text    AS arrival_time,
                t.available_seats,
                orig.id   AS origin_id,   orig.code  AS origin_code,
                orig.name AS origin_name,  orig.city  AS origin_city,
                orig.state AS origin_state,
                dest.id   AS dest_id,     dest.code  AS dest_code,
                dest.name AS dest_name,    dest.city  AS dest_city,
                dest.state AS dest_state,
                COALESCE(fa.price_cents, 0) AS adult_price_cents,
                COALESCE(fc.price_cents, 0) AS child_price_cents
            FROM trips t
            JOIN schedules s   ON s.id = t.schedule_id
            JOIN routes r      ON r.id = s.route_id
            JOIN stations orig ON orig.id = r.origin_id
            JOIN stations dest ON dest.id = r.destination_id
            LEFT JOIN fare_rules fa
                ON fa.route_id = r.id AND fa.passenger_type = 'adult'
                AND fa.effective_from <= t.date
                AND (fa.effective_until IS NULL OR fa.effective_until >= t.date)
            LEFT JOIN fare_rules fc
                ON fc.route_id = r.id AND fc.passenger_type = 'child'
                AND fc.effective_from <= t.date
                AND (fc.effective_until IS NULL OR fc.effective_until >= t.date)
            WHERE orig.code = %(origin)s
              AND dest.code = %(destination)s
              AND t.date = %(date)s
              AND t.status = 'scheduled'
              AND t.available_seats > 0
              AND s.is_active = true
            ORDER BY s.departure_time
            """,
            {"origin": origin, "destination": destination, "date": date},
        )
        rows = await cur.fetchall()

    return [
        {
            "id": r["id"],
            "date": r["date"],
            "departure_time": r["departure_time"][:5],
            "arrival_time": r["arrival_time"][:5],
            "available_seats": r["available_seats"],
            "origin": {
                "id": r["origin_id"],
                "code": r["origin_code"],
                "name": r["origin_name"],
                "city": r["origin_city"],
                "state": r["origin_state"],
            },
            "destination": {
                "id": r["dest_id"],
                "code": r["dest_code"],
                "name": r["dest_name"],
                "city": r["dest_city"],
                "state": r["dest_state"],
            },
            "fares": {
                "adult_price_cents": r["adult_price_cents"],
                "child_price_cents": r["child_price_cents"],
            },
        }
        for r in rows
    ]
