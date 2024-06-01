from datetime import date

from pydantic import BaseModel


class SBooking(BaseModel):

    id: int
    room_id: int
    user_id: int
    date_from: date
    date_to: date
    price: float
    total_cost: float
    total_days: int
    image_id: int
    # Room params
    name: str
    description: str
    services: list
