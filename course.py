import logging
from json import loads
from typing import Callable

from httpx import URL
from websockets.exceptions import ConnectionClosed
from websockets.sync.client import connect

from settings import settings

handlers: list[Callable[[list[tuple[float, float]] | None], None]] = []


def listen_course(token: str, ship_id: int) -> None:
    url = URL(settings.base_url).join("/ship/listen/course")
    url = url.copy_with(
        scheme="wss" if url.scheme == "https" else "ws",
        params=dict(
            token=token,
            id=ship_id,
        ),
    )

    with connect(str(url)) as ws:
        for msg in ws:
            course: list[tuple[float, float]] | None = loads(msg)
            for handler in handlers:
                handler(course)


def on_course_update(func: Callable[[list[tuple[float, float]] | None], None]) -> None:
    handlers.append(func)
