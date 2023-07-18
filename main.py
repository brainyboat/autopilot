import logging
import time
from math import isnan
from multiprocessing import Process

import httpx

from camera import camera_record
from course import listen_course
from models import Ship
from settings import settings
from telemetry import get_telemetry, listen_telemetry, send_telemetry


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

token = login(client)
client.headers["X-Token"] = token
ship = get_ship_id(client)
logging.info(f"Name of this ship: {ship.name}")

listen_telemetry_process = Process(target=listen_telemetry, args=(1,))
listen_telemetry_process.start()

logging.info("Wait telemetry normalization")

telemetry = get_telemetry()
while (
    isnan(telemetry.longitude)
    or isnan(telemetry.longitude)
    or isnan(telemetry.angle)
    or isnan(telemetry.temperature)
    or isnan(telemetry.voltage)
    or isnan(telemetry.velocity)
):
    telemetry = get_telemetry()
    time.sleep(1)

camera_record_process = Process(target=camera_record, args=())
listen_course_process = Process(target=listen_course, args=(token, ship.id))
send_telemetry_process = Process(target=send_telemetry, args=(client, ship.id, 1))

send_telemetry_process.start()
listen_course_process.start()
camera_record_process.start()

camera_record_process.join()
