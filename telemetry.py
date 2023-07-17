import io
import time
from datetime import datetime
from multiprocessing import Value

import httpx
import pynmea2
from serial import Serial

from models import AddTelemetry, Telemetry

longitude = Value("f", float("nan"))
latitude = Value("f", float("nan"))
angle = Value("f", float("nan"))
temperature = Value("f", float("nan"))
voltage = Value("f", -1)
velocity = Value("f", float("nan"))


def get_telemetry() -> Telemetry:
    return Telemetry(
        longitude=longitude.value,  # type: ignore[attr-defined]
        latitude=latitude.value,  # type: ignore[attr-defined]
        angle=angle.value,  # type: ignore[attr-defined]
        temperature=temperature.value,  # type: ignore[attr-defined]
        voltage=voltage.value,  # type: ignore[attr-defined]
        velocity=velocity.value,  # type: ignore[attr-defined]
    )


def listen_telemetry(thermal_zone: int = 1) -> None:
    gps_serial = io.TextIOWrapper(
        Serial(
            "/dev/ttyUSB0",
            9600,
            timeout=0.5,
        )
    )

    while True:
        try:
            gps = pynmea2.parse(gps_serial.readline())
        except Exception:
            continue

        if isinstance(gps, pynmea2.GGA):
            if gps.lon:
                longitude.value = float(gps.longitude)  # type: ignore[attr-defined]
            if gps.lat:
                latitude.value = float(gps.latitude)  # type: ignore[attr-defined]

        if isinstance(gps, pynmea2.VTG):
            if gps.spd_over_grnd_kmph is not None:
                velocity.value = float(gps.spd_over_grnd_kmph)  # type: ignore[attr-defined]

            if gps.true_track is not None:
                angle.value = float(gps.true_track)  # type: ignore[attr-defined]

        with open(
            f"/sys/class/thermal/thermal_zone{thermal_zone}/temp"
        ) as temperature_file:
            temperature.value = int(temperature_file.read()) / 1000  # type: ignore[attr-defined]


def send_telemetry(client: httpx.Client, ship_id: int, delay: int = 1) -> None:
    while True:
        telemetry = get_telemetry()
        client.post(
            "/telemetry/add",
            json=AddTelemetry(
                longitude=telemetry.longitude,
                latitude=telemetry.latitude,
                angle=telemetry.angle,
                temperature=telemetry.temperature,
                voltage=telemetry.voltage,
                velocity=telemetry.velocity,
                ship_id=ship_id,
                datetime=datetime.utcnow(),
            ).model_dump(mode="json"),
        )
        time.sleep(delay)
