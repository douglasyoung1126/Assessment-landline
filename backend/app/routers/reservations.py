from fastapi import APIRouter, Depends, HTTPException
from psycopg_pool import AsyncConnectionPool

from app.database import get_pool
from app.schemas import ReservationCreate
from app.services.booking import create_reservation, cancel_reservation, lookup_reservation

router = APIRouter(tags=["reservations"])


@router.post("/reservations", status_code=201)
async def book(
    payload: ReservationCreate,
    pool: AsyncConnectionPool = Depends(get_pool),
):
    if not payload.passengers:
        raise HTTPException(400, "At least one passenger is required")
    return await create_reservation(pool, payload)


@router.get("/reservations/{confirmation_code}")
async def get_reservation(
    confirmation_code: str,
    pool: AsyncConnectionPool = Depends(get_pool),
):
    result = await lookup_reservation(pool, confirmation_code.upper())
    if not result:
        raise HTTPException(404, "Reservation not found")
    return result


@router.post("/reservations/{confirmation_code}/cancel")
async def cancel(
    confirmation_code: str,
    pool: AsyncConnectionPool = Depends(get_pool),
):
    return await cancel_reservation(pool, confirmation_code.upper())
