from __future__ import annotations

from course import on_course_update


@on_course_update
def autopilot(course: list[tuple[float, float]] | None) -> None:
    pass
