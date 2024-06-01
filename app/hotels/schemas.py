from pydantic import BaseModel, ConfigDict


class SHotel(BaseModel):
    id: int
    name: str
    location: str
    services: list[str]
    rooms_quantity: int
    image_id: int


class SAvailableHotel(SHotel):
    model_config = ConfigDict(from_attributes=True)
    rooms_left: int
