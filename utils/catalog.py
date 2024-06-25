import aiohttp
import re
import cv2
import pytesseract
import numpy as np
from PIL import Image
from io import BytesIO

from models.semester import Semester
from models.course import Course
from models.exam import Exam

from utils.cas import cas_login_data
from utils.constants import cas_login_headers
from utils.constants import catalog_headers as catalog_headers
from utils.constants import normal_headers as headers
from utils.tools import raw_date_to_unix_timestamp


async def login(session: aiohttp.ClientSession):
    url = "https://passport.ustc.edu.cn/login"
    await session.get(
        url,
        headers=headers,
        allow_redirects=False,
    )

    url = "https://passport.ustc.edu.cn/login?service=https://catalog.ustc.edu.cn/ustc_cas_login?next=https://catalog.ustc.edu.cn/query/lesson"
    response = await session.get(
        url=url,
        allow_redirects=False,
    )
    text = await response.text()

    # if response is 302, then we are already logged in:
    if response.status == 302:
        url = response.headers["Location"]
        if not url.startswith(
            "https://catalog.ustc.edu.cn/ustc_cas_login?next=https://catalog.ustc.edu.cn/query/lesson&ticket="
        ):
            raise Exception("Login failed")
        response = await session.get(url=url, headers=headers, allow_redirects=False)
        return

    token_pattern = re.compile(r"LT-[a-z0-9]+")
    cas_lt = token_pattern.findall(text)[0]

    url = "https://passport.ustc.edu.cn/validatecode.jsp?type=login"
    response = await session.get(
        url=url,
    )
    image = Image.open(BytesIO(await response.read()))
    image = cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2GRAY)
    kernel = np.ones((3, 3), np.uint8)
    image = cv2.dilate(image, kernel, iterations=1)
    image = cv2.erode(image, kernel, iterations=1)
    lt = pytesseract.image_to_string(Image.fromarray(image))[0:4]

    url = "https://passport.ustc.edu.cn/login"
    response = await session.post(
        url=url,
        data=cas_login_data(
            cas_lt,
            lt,
            service="https://catalog.ustc.edu.cn/ustc_cas_login?next=https://catalog.ustc.edu.cn/query/lesson",
        ),
        allow_redirects=False,
    )

    url = response.headers["Location"]
    if not url.startswith(
        "https://catalog.ustc.edu.cn/ustc_cas_login?next=https://catalog.ustc.edu.cn/query/lesson&ticket="
    ):
        raise Exception("Login failed")
    response = await session.get(url=url, headers=headers, allow_redirects=False)
    return


async def get_semesters(session: aiohttp.ClientSession) -> list[Semester]:
    url = "https://catalog.ustc.edu.cn/api/teach/semester/list"

    response = await session.get(
        url=url, headers=catalog_headers, allow_redirects=False
    )
    json = await response.json()

    # convert json to Semester

    result = []
    for semester_json in json:
        result.append(
            Semester(
                id=str(semester_json["id"]),
                courses=[],
                name=semester_json["nameZh"],
                startDate=raw_date_to_unix_timestamp(semester_json["start"]),
                endDate=raw_date_to_unix_timestamp(semester_json["end"]),
            )
        )
    return result


async def get_courses(session: aiohttp.ClientSession, semester_id: str) -> list[Course]:
    url = "https://catalog.ustc.edu.cn/api/teach/lesson/list-for-teach/" + semester_id

    response = await session.get(
        url=url,
        headers=catalog_headers,
        allow_redirects=False,
    )
    json = await response.json()

    # convert json to Course

    result = []
    for course_json in json:
        teacher_name_list = [
            teacher["cn"] for teacher in course_json["teacherAssignmentList"]
        ]
        # strip None:
        teacher_name_list = [
            teacher_name for teacher_name in teacher_name_list if teacher_name
        ]
        teachers = ", ".join(teacher_name_list)
        result.append(
            Course(
                id=course_json["id"],
                name=course_json["course"]["cn"],
                courseCode=course_json["course"]["code"],
                lessonCode=course_json["code"],
                teacherName=teachers,
                lectures=[],
                exams=[],
                dateTimePlacePersonText=course_json["dateTimePlacePersonText"]["cn"],
                courseType=course_json["courseType"]["cn"],
                courseGradation=course_json["courseGradation"]["cn"],
                courseCategory=course_json["courseCategory"]["cn"],
                educationType=course_json["education"]["cn"],
                classType=course_json["classType"]["cn"],
                openDepartment=course_json["openDepartment"]["cn"],
                description="",
                credit=course_json["credits"],
                additionalInfo={},
            )
        )
    return result


async def get_exams(
    session: aiohttp.ClientSession,
    semester_id: str,
) -> dict[str, list[Exam]]:
    url = "https://catalog.ustc.edu.cn/api/teach/exam/list/" + semester_id

    response = await session.get(
        url=url,
        headers=catalog_headers,
        allow_redirects=False,
    )
    json = await response.json()

    result = {}
    for exam_json in json:
        room_list = [room["room"] for room in exam_json["examRooms"]]
        location = ", ".join(room_list)

        date = raw_date_to_unix_timestamp(exam_json["examDate"])
        startHHMM = int(exam_json["startTime"])
        endHHMM = int(exam_json["endTime"])

        startDate = date + int(startHHMM // 100) * 3600 + int(startHHMM % 100) * 60
        endDate = date + int(endHHMM // 100) * 3600 + int(endHHMM % 100) * 60

        examType = "Unknown"
        if exam_json["examType"] == 1:
            examType = "期中考试"
        elif exam_json["examType"] == 2:
            examType = "期末考试"
        examMode = exam_json["examMode"]

        name = exam_json["lesson"]["course"]["cn"]
        id = exam_json["lesson"]["id"]

        exam = Exam(
            startDate=startDate,
            endDate=endDate,
            name=name,
            location=location,
            examType=examType,
            startHHMM=startHHMM,
            endHHMM=endHHMM,
            examMode=examMode,
            additionalInfo={},
        )
        if id in result:
            result[id].append(exam)
        else:
            result[id] = [exam]

    return result
