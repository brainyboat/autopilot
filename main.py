import logging

import httpx

from models import Ship
from settings import settings
from telemetry import send_telemetry


def login(client: httpx.Client) -> str:
    response = client.post(
        "/user/login",
        json=dict(
            username=settings.username,
            password=settings.password,
        ),
    )

    if response.status_code != 200:
        raise RuntimeError("Logging error")

    return response.json()["token"]


def get_ship_id(client: httpx.Client) -> Ship:
    response = client.get("/ship/get/imai", params=dict(imai=settings.imai))

    if response.status_code != 200:
        raise RuntimeError("Ship getting error")

    return Ship.model_validate(response.json())


logging.basicConfig(level=logging.INFO)
client = httpx.Client(base_url=settings.base_url)

client.headers["X-Token"] = login(client)
ship = get_ship_id(client)

logging.info(f"Name of this ship: {ship.name}")

send_telemetry(client, ship.id)
