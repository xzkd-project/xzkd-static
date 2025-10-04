import datetime
from models import course


class Semester:
    id: str
    courses: list[course.Course]
    name: str
    startDate: int  # unix timestamp
    endDate: int  # unix timestamp

    def __init__(
        self,
        id: str,
        courses: list[course.Course],
        name: str,
        startDate: int,
        endDate: int,
    ):
        self.id = id
        self.courses = courses
        self.name = name
        self.startDate = startDate
        self.endDate = endDate

    def __str__(self) -> str:
        start_date = datetime.datetime.fromtimestamp(self.startDate).strftime(
            "%Y-%m-%d"
        )
        end_date = datetime.datetime.fromtimestamp(self.endDate).strftime("%Y-%m-%d")
        return f"Semester(id={self.id}, name={self.name}, {start_date} - {end_date})"
