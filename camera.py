import logging
import time
import zipfile
from csv import writer
from datetime import datetime
from itertools import count

import cv2

from telemetry import get_telemetry


def gstreamer_pipeline(
    sensor_id=0,
    capture_width=1920,
    capture_height=1080,
    display_width=1920,
    display_height=1080,
    framerate=60,
    flip_method=0,
) -> str:
    return (
        f"nvarguscamerasrc sensor-id={sensor_id} ! "
        f"video/x-raw(memory:NVMM), width=(int){capture_width}, height=(int){capture_height}, framerate=(fraction){framerate}/1 ! "
        f"nvvidconv flip-method={flip_method} ! "
        f"video/x-raw, width=(int){display_width}, height=(int){display_height}, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
    )


def camera_record() -> None:
    archive = zipfile.ZipFile("dataset.zip", "w", compression=zipfile.ZIP_STORED)
    csv_file = open("dataset.csv")
    csv = writer(csv_file)

    camera1 = cv2.VideoCapture(gstreamer_pipeline(0), cv2.CAP_GSTREAMER)
    camera2 = cv2.VideoCapture(gstreamer_pipeline(1), cv2.CAP_GSTREAMER)

    start = time.time()
    csv.writerows(
        (
            "id",
            "latitude",
            "longitude",
            "angle",
            "velocity",
            "second",
            "datetime",
        )
    )

    if not camera1.isOpened():
        print("Camera 1 not working")
    if not camera2.isOpened():
        print("Camera 2 not working")

    try:
        for num in count():
            img1, img2 = camera1.read()[1], camera2.read()[1]

            with archive.open(f"image_0/{num:0>6}.png", "w") as img_file:
                img_file.write(cv2.imencode(".png", img1)[1])  # type: ignore[call-overload]

            with archive.open(f"image_1/{num:0>6}.png", "w") as img_file:
                img_file.write(cv2.imencode(".png", img2)[1])  # type: ignore[call-overload]

            telemetry = get_telemetry()
            csv.writerow(
                (
                    num,
                    telemetry.latitude,
                    telemetry.longitude,
                    telemetry.angle,
                    telemetry.velocity,
                    time.time() - start,
                    datetime.now(),
                )
            )
            logging.info(f"Image {num} recorded")
    finally:
        camera1.release()
        camera2.release()
        archive.close()
        csv_file.close()
