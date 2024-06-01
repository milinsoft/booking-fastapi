from pydantic import BaseModel


class SRoom(BaseModel):
    id: int
    hotel_id: int
    name: str
    description: str
    services: list[str]
    price: float
    quantity: int
    image_id: int
    total_price: float
    rooms_left: int
