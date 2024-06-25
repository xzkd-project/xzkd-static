from models.lecture import Lecture
from models.exam import Exam


class Course:
    id: str
    name: str
    courseCode: str
    lessonCode: str
    teacherName: str
    lectures: list[Lecture]
    exams: list[Exam]
    dateTimePlacePersonText: str
    courseType: str
    courseGradation: str
    courseCategory: str
    educationType: str
    classType: str
    openDepartment: str
    description: str
    credit: float
    additionalInfo: dict[str, str]

    def __init__(
        self,
        id: str,
        name: str,
        courseCode: str,
        lessonCode: str,
        teacherName: str,
        lectures: list[Lecture],
        exams: list[Exam],
        dateTimePlacePersonText: str,
        courseType: str,
        courseGradation: str,
        courseCategory: str,
        educationType: str,
        classType: str,
        openDepartment: str,
        description: str,
        credit: float,
        additionalInfo: dict[str, str],
    ):
        self.id = id
        self.name = name
        self.courseCode = courseCode
        self.lessonCode = lessonCode
        self.teacherName = teacherName
        self.lectures = lectures
        self.exams = exams
        self.dateTimePlacePersonText = dateTimePlacePersonText
        self.courseType = courseType
        self.courseGradation = courseGradation
        self.courseCategory = courseCategory
        self.educationType = educationType
        self.classType = classType
        self.openDepartment = openDepartment
        self.description = description
        self.credit = credit
        self.additionalInfo = additionalInfo
