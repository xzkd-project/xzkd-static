import re

from io import BytesIO
from PIL import Image
import cv2
import numpy as np
import pytesseract

import aiohttp

from models.course import Course
from models.lecture import Lecture

from utils.cas import cas_login_data
from utils.constants import cas_login_headers
from utils.constants import normal_headers as headers
from utils.tools import raw_date_to_unix_timestamp


async def login(session: aiohttp.ClientSession):
    url = "https://jw.ustc.edu.cn/"
    await session.get(
        url,
        headers=headers,
        allow_redirects=False
    )

    url = "https://jw.ustc.edu.cn/ucas-sso/login"
    await session.get(
        url=url,
        headers=headers,
        allow_redirects=False
    )

    url = "https://passport.ustc.edu.cn/login?service=https%3A%2F%2Fjw.ustc.edu.cn%2Fucas-sso%2Flogin"
    token_pattern = re.compile(r"LT-[a-z0-9]+")
    response = await session.get(
        url=url,
        allow_redirects=False
    )
    text = await response.text()
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
        data=cas_login_data(cas_lt, lt),
        allow_redirects=False
    )

    url = response.headers["Location"]
    response = await session.get(
        url=url,
        headers=headers,
        allow_redirects=False
    )

    url = response.headers["Location"]
    if not url == "https://jw.ustc.edu.cn/":
        raise Exception("Login failed")

indexStartTimes: dict[int: int] = {
    1: 7 * 60 + 50,
    2: 8 * 60 + 40,
    3: 9 * 60 + 45,
    4: 10 * 60 + 35,
    5: 11 * 60 + 25,
    6: 14 * 60 + 0,
    7: 14 * 60 + 50,
    8: 15 * 60 + 35,
    9: 16 * 60 + 45,
    10: 17 * 60 + 35,
    11: 19 * 60 + 30,
    12: 20 * 60 + 20,
    13: 21 * 60 + 10
}

# 0835 0925 0945 1030 1120 1445 1535 1555 1640 1730 2015 2105 2155
endIndexTimes: dict[int: int] = {
    1: 8 * 60 + 35,
    2: 9 * 60 + 25,
    3: 10 * 60 + 30,
    4: 11 * 60 + 20,
    5: 12 * 60 + 10,
    6: 14 * 60 + 45,
    7: 15 * 60 + 35,
    8: 16 * 60 + 40,
    9: 17 * 60 + 30,
    10: 18 * 60 + 20,
    11: 20 * 60 + 15,
    12: 21 * 60 + 5,
    13: 21 * 60 + 55
}


def findNearestIndex(time: int, times: dict[int: int]) -> int:
    map = {}
    for index, t in times.items():
        map[abs(time - t)] = index
    return map[min(map.keys())]


def cleanLectures(lectures: list[Lecture]) -> list[Lecture]:
    """
    This handles the following situations:

    1. At the same time & place, sometimes jw.u.e.c would return two lectures, but with different teacher names, combine them as one.
    2. A Lecture taking place in non conventional time, for example 19:00 - 21:00 would be split into two lectures, combine them as one.
    """
    result = []

    for lecture in lectures:
        for r in result:
            if lecture.startDate >= r.startDate and lecture.location == r.location and lecture.endDate <= r.endDate:
                r.teacherName += "," + lecture.teacherName
                break
            elif lecture.endDate == r.startDate:
                r.startDate = lecture.startDate
                r.startIndex = lecture.startIndex
                break
            elif lecture.startDate == r.endDate:
                r.endDate = lecture.endDate
                r.endIndex = lecture.endIndex
                break
        else:
            result.append(lecture)


async def update_lectures(session: aiohttp.ClientSession, course_list: list[Course]) -> list[Course]:
    course_id_list = [course.id for course in course_list]
    url = "https://jw.ustc.edu.cn/ws/schedule-table/datum"
    data = {
        "lessonIds": course_id_list,
    }
    _headers = headers | {
        "Accept": "*/*",
        "Content-Type": "application/json;charset=UTF-8",
    }
    r = await session.post(
        url=url,
        headers=_headers,
        json=data,
        allow_redirects=False
    )
    json = await r.json()
    json = json["result"]

    for schedule_json in json["scheduleList"]:
        course = [course for course in course_list if course.id ==
                  schedule_json["lessonId"]][0]

        date = raw_date_to_unix_timestamp(schedule_json["date"])
        startHHMM = int(schedule_json["startTime"])
        endHHMM = int(schedule_json["endTime"])

        startDate = date + int(startHHMM // 100) * \
            3600 + int(startHHMM % 100) * 60
        endDate = date + int(endHHMM // 100) * 3600 + int(endHHMM % 100) * 60

        location = schedule_json["room"]["nameZh"] if schedule_json["room"] else schedule_json["customPlace"]

        startIndex = findNearestIndex(
            int(startHHMM // 100) * 60 + int(startHHMM % 100), indexStartTimes)
        endIndex = findNearestIndex(
            int(endHHMM // 100) * 60 + int(endHHMM % 100), endIndexTimes)

        lecture = Lecture(
            startDate=startDate,
            endDate=endDate,
            name=course.name,
            location=location,
            teacherName=schedule_json["personName"],
            periods=schedule_json["periods"],
            additionalInfo={},
            startIndex=startIndex,
            endIndex=endIndex
        )

        for course in course_list:
            if course.id == schedule_json["lessonId"]:
                course.lectures.append(lecture)
                break

    for course in course_list:
        course.lectures = cleanLectures(course.lectures)

    return course_list
