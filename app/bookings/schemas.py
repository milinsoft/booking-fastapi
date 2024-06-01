from datetime import date

from pydantic import BaseModel, ConfigDict


class SBooking(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    room_id: int
    user_id: int
    date_from: date
    date_to: date
    price: float
    total_cost: float
    total_days: int


class SBookingInfo(SBooking):
    # Room params
    image_id: int
    # Room params
    name: str
    description: str | None
    services: list[str]
