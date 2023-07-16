import io
from datetime import datetime

import httpx
import pynmea2
from serial import Serial

from models import Telemetry

prev_angle: float | None = None


def get_gps_telemetry(
    max_dilution: float = 5,
    min_velocity: float = 1,
) -> tuple[float, float, float, float]:
    global prev_angle
    lon = lat = velocity = angle = None
    gps = io.TextIOWrapper(
        Serial(
            "/dev/ttyUSB0",
            9600,
            timeout=1,
        )
    )

    while lon is None or lat is None or velocity is None or angle is None:
        try:
            msg = pynmea2.parse(gps.readline())
        except Exception:
            continue

        if isinstance(msg, pynmea2.GGA):
            if float(msg.horizontal_dil) <= max_dilution:
                lon = float(msg.longitude)
                lat = float(msg.latitude)
        elif isinstance(msg, pynmea2.VTG):
            if (
                msg.spd_over_grnd_kmph is not None
                and float(msg.spd_over_grnd_kmph) >= min_velocity
            ):
                velocity = float(msg.spd_over_grnd_kmph)

            if msg.true_track is not None:
                angle = float(msg.true_track)
                prev_angle = angle
            elif prev_angle is not None:
                angle = prev_angle

    return lon, lat, velocity, angle


def get_system_telemetry(thermal_zone: int) -> tuple[float, float]:
    with open(
        f"/sys/class/thermal/thermal_zone{thermal_zone}/temp"
    ) as temperature_file:
        temperature = int(temperature_file.read()) / 1000

    return temperature, -1


def send_telemetry(client: httpx.Client, ship_id: int) -> None:
    while True:
        lon, lat, velocity, angle = get_gps_telemetry(5, 1.5)
        temperature, voltage = get_system_telemetry(1)

        telemetry = Telemetry(
            ship_id=ship_id,
            datetime=datetime.now(),
            longitude=lon,
            latitude=lat,
            angle=angle,
            temperature=temperature,
            voltage=voltage,
            velocity=velocity,
        )

        client.post("/telemetry/add", json=telemetry.model_dump(mode="json"))
