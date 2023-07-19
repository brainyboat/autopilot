from typing import Optional
from datetime import datetime
from typing import List, Tuple

from pydantic import BaseModel


class User(BaseModel):
    id: int
    username: str


class Ship(BaseModel):
    id: int
    imai: int
    course: Optional[List[Tuple[float, float]]]
    name: str
    color: str
    owner: User


class Telemetry(BaseModel):
    longitude: float
    latitude: float
    angle: float
    temperature: float
    voltage: float
    velocity: float


class AddTelemetry(Telemetry):
    ship_id: int
    datetime: datetime
