import aiohttp

from models.semester import Semester
from models.course import Course

from utils.constants import catalog_headers as headers
from utils.tools import raw_date_to_unix_timestamp


async def get_semesters() -> list[Semester]:
    url = "https://catalog.ustc.edu.cn/api/teach/semester/list"
    async with aiohttp.ClientSession() as session:
        response = await session.get(
            url=url,
            headers=headers,
            allow_redirects=False
        )
        json = await response.json()

    # convert json to Semester

    result = []
    for semester_json in json:
        result.append(Semester(
            id=str(semester_json["id"]),
            courses=[],
            name=semester_json["nameZh"],
            startDate=raw_date_to_unix_timestamp(semester_json["start"]),
            endDate=raw_date_to_unix_timestamp(semester_json["end"])
        ))
    return result


async def get_courses(semester_id: str) -> list[Course]:
    url = "https://catalog.ustc.edu.cn/api/teach/lesson/list-for-teach/" + semester_id
    async with aiohttp.ClientSession() as session:
        response = await session.get(
            url=url,
            headers=headers,
            allow_redirects=False
        )
        json = await response.json()

    # convert json to Course

    result = []
    for course_json in json:
        teacher_name_list = [teacher["cn"]
                             for teacher in course_json["teacherAssignmentList"]]
        # strip None:
        teacher_name_list = [
            teacher_name for teacher_name in teacher_name_list if teacher_name]
        teachers = ", ".join(teacher_name_list)
        result.append(Course(
            id=course_json["id"],
            name=course_json["course"]["cn"],
            courseCode=course_json["course"]["code"],
            lessonCode=course_json["code"],
            teacherName=teachers,
            lectures=[],
            description=course_json["dateTimePlacePersonText"]["cn"],
            credit=course_json["credits"],
            additionalInfo={}
        ))
    return result
