from models import course


class Semester:
    id: str
    courses: list[course.Course]
    name: str
    startDate: int  # unix timestamp
    endDate: int  # unix timestamp

    def __init__(self, id: str, courses: list[course.Course], name: str, startDate: int, endDate: int):
        self.id = id
        self.courses = courses
        self.name = name
        self.startDate = startDate
        self.endDate = endDate
