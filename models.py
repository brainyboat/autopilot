from datetime import datetime

from pydantic import BaseModel


class User(BaseModel):
    id: int
    username: str


class Ship(BaseModel):
    id: int
    imai: int
    course: list[tuple[float, float]] | None
    name: str
    color: str
    owner: User


class Telemetry(BaseModel):
    ship_id: int
    datetime: datetime
    longitude: float
    latitude: float
    angle: float
    temperature: float
    voltage: float
    velocity: float
