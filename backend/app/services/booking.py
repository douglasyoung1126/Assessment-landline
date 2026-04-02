"""
Booking service — owns the critical write path.

Concurrency strategy:
  SELECT ... FOR UPDATE on the trips row serializes concurrent bookings
  for the same trip.  The CHECK(available_seats >= 0) constraint on the
  trips table is the ultimate safety net against overbooking.
"""

import logging
import random
import string

from fastapi import HTTPException
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

from app.schemas import ReservationCreate

logger = logging.getLogger(__name__)


def _generate_code() -> str:
    chars = string.ascii_uppercase + string.digits
    return "LND-" + "".join(random.choices(chars, k=6))


async def create_reservation(
    pool: AsyncConnectionPool,
    payload: ReservationCreate,
):
    seat_count = len(payload.passengers)

    async with pool.connection() as conn:
        conn.row_factory = dict_row
        async with conn.transaction():
            # ── 1. Lock trip row, verify availability ──────────────────
            cur = await conn.execute(
                """
                SELECT t.id, t.available_seats, t.version, t.date,
                       s.departure_time::text AS departure_time,
                       s.arrival_time::text   AS arrival_time,
                       r.id AS route_id,
                       orig.name AS origin_name,
                       dest.name AS dest_name
                FROM trips t
                JOIN schedules s   ON s.id = t.schedule_id
                JOIN routes r      ON r.id = s.route_id
                JOIN stations orig ON orig.id = r.origin_id
                JOIN stations dest ON dest.id = r.destination_id
                WHERE t.id = %s AND t.status = 'scheduled'
                FOR UPDATE OF t
                """,
                [payload.trip_id],
            )
            trip = await cur.fetchone()

            if not trip:
                raise HTTPException(404, "Trip not found")
            if trip["available_seats"] < seat_count:
                raise HTTPException(
                    409,
                    f"Only {trip['available_seats']} seat(s) remaining",
                )

            # ── 2. Look up fares for this route / date ─────────────────
            cur = await conn.execute(
                """
                SELECT passenger_type::text, price_cents
                FROM fare_rules
                WHERE route_id = %s
                  AND effective_from <= %s
                  AND (effective_until IS NULL OR effective_until >= %s)
                """,
                [trip["route_id"], trip["date"], trip["date"]],
            )
            fare_map = {r["passenger_type"]: r["price_cents"] async for r in cur}

            total_cents = 0
            passenger_prices: list[int] = []
            for p in payload.passengers:
                price = fare_map.get(p.passenger_type, 0)
                passenger_prices.append(price)
                total_cents += price

            # ── 3. Decrement available seats ───────────────────────────
            await conn.execute(
                """
                UPDATE trips
                SET available_seats = available_seats - %s,
                    version = version + 1
                WHERE id = %s AND version = %s
                """,
                [seat_count, trip["id"], trip["version"]],
            )

            # ── 4. Generate unique confirmation code ───────────────────
            code = _generate_code()
            for _ in range(5):
                dup = await conn.execute(
                    "SELECT 1 FROM reservations WHERE confirmation_code = %s",
                    [code],
                )
                if not await dup.fetchone():
                    break
                code = _generate_code()

            # ── 5. Insert reservation ──────────────────────────────────
            cur = await conn.execute(
                """
                INSERT INTO reservations
                    (trip_id, confirmation_code, contact_email,
                     contact_phone, total_cents, seat_count, status)
                VALUES (%s, %s, %s, %s, %s, %s, 'confirmed')
                RETURNING id, booked_at::text
                """,
                [
                    trip["id"],
                    code,
                    payload.contact_email,
                    payload.contact_phone,
                    total_cents,
                    seat_count,
                ],
            )
            res_row = await cur.fetchone()
            reservation_id = res_row["id"]

            # ── 6. Insert passengers ───────────────────────────────────
            passengers_out = []
            for i, p in enumerate(payload.passengers):
                await conn.execute(
                    """
                    INSERT INTO passengers
                        (reservation_id, first_name, last_name,
                         passenger_type, price_cents)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    [
                        reservation_id,
                        p.first_name,
                        p.last_name,
                        p.passenger_type,
                        passenger_prices[i],
                    ],
                )
                passengers_out.append(
                    {
                        "first_name": p.first_name,
                        "last_name": p.last_name,
                        "passenger_type": p.passenger_type,
                        "price_cents": passenger_prices[i],
                    }
                )

            logger.info(
                "Booking created: %s — trip %s, %d seat(s)",
                code,
                trip["id"],
                seat_count,
            )

            return {
                "confirmation_code": code,
                "status": "confirmed",
                "trip_date": str(trip["date"]),
                "departure_time": trip["departure_time"][:5],
                "arrival_time": trip["arrival_time"][:5],
                "origin": trip["origin_name"],
                "destination": trip["dest_name"],
                "contact_email": payload.contact_email,
                "contact_phone": payload.contact_phone,
                "passengers": passengers_out,
                "total_cents": total_cents,
                "booked_at": res_row["booked_at"],
            }


async def cancel_reservation(
    pool: AsyncConnectionPool,
    confirmation_code: str,
):
    async with pool.connection() as conn:
        conn.row_factory = dict_row
        async with conn.transaction():
            cur = await conn.execute(
                """
                SELECT id, status, seat_count, trip_id
                FROM reservations
                WHERE confirmation_code = %s
                FOR UPDATE
                """,
                [confirmation_code],
            )
            res = await cur.fetchone()

            if not res:
                raise HTTPException(404, "Reservation not found")
            if res["status"] == "cancelled":
                return {
                    "confirmation_code": confirmation_code,
                    "status": "cancelled",
                    "message": "Already cancelled",
                }

            await conn.execute(
                "UPDATE reservations SET status = 'cancelled', cancelled_at = now() WHERE id = %s",
                [res["id"]],
            )
            await conn.execute(
                "UPDATE trips SET available_seats = available_seats + %s, version = version + 1 WHERE id = %s",
                [res["seat_count"], res["trip_id"]],
            )

            logger.info("Reservation cancelled: %s", confirmation_code)
            return {
                "confirmation_code": confirmation_code,
                "status": "cancelled",
            }


async def lookup_reservation(
    pool: AsyncConnectionPool,
    confirmation_code: str,
):
    async with pool.connection() as conn:
        conn.row_factory = dict_row
        cur = await conn.execute(
            """
            SELECT
                r.confirmation_code, r.status,
                r.contact_email, r.contact_phone,
                r.total_cents, r.booked_at::text,
                t.date::text            AS trip_date,
                s.departure_time::text  AS departure_time,
                s.arrival_time::text    AS arrival_time,
                orig.name AS origin,
                dest.name AS destination
            FROM reservations r
            JOIN trips t       ON t.id = r.trip_id
            JOIN schedules s   ON s.id = t.schedule_id
            JOIN routes rt     ON rt.id = s.route_id
            JOIN stations orig ON orig.id = rt.origin_id
            JOIN stations dest ON dest.id = rt.destination_id
            WHERE r.confirmation_code = %s
            """,
            [confirmation_code],
        )
        reservation = await cur.fetchone()
        if not reservation:
            return None

        cur = await conn.execute(
            """
            SELECT first_name, last_name, passenger_type::text, price_cents
            FROM passengers
            WHERE reservation_id = (
                SELECT id FROM reservations WHERE confirmation_code = %s
            )
            """,
            [confirmation_code],
        )
        passengers = await cur.fetchall()

        reservation["passengers"] = passengers
        reservation["departure_time"] = reservation["departure_time"][:5]
        reservation["arrival_time"] = reservation["arrival_time"][:5]
        return reservation
