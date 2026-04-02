from typing import Literal
from pydantic import BaseModel, EmailStr


class PassengerCreate(BaseModel):
    first_name: str
    last_name: str
    passenger_type: Literal["adult", "child"] = "adult"


class ReservationCreate(BaseModel):
    trip_id: int
    contact_email: EmailStr
    contact_phone: str | None = None
    passengers: list[PassengerCreate]
