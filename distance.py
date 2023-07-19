import json
from multiprocessing import Value

from websockets.sync.client import connect

distance = Value("i", 0)


def get_distance() -> int:
    return distance.value  # type:ignore [attr-defined]


def listen_distance() -> None:
    with connect("ws://192.168.8.101:8001") as con:
        for msg in con:
            distance.value = json.loads(msg)  # type:ignore [attr-defined]
