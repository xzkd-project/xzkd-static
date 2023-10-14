from models import lecture


class Course:
    id: str
    name: str
    courseCode: str
    lessonCode: str
    teacherName: str
    lectures: list[lecture.Lecture]
    description: str
    credit: float
    additionalInfo: dict[str, str]

    def __init__(self, id: str, name: str, courseCode: str, lessonCode: str, teacherName: str,
                 lectures: list[lecture.Lecture], description: str, credit: float, additionalInfo: dict[str, str]):
        self.id = id
        self.name = name
        self.courseCode = courseCode
        self.lessonCode = lessonCode
        self.teacherName = teacherName
        self.lectures = lectures
        self.description = description
        self.credit = credit
        self.additionalInfo = additionalInfo
