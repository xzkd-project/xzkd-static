import re

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
        headers=headers,
        allow_redirects=False
    )
    text = await response.text()
    lt = token_pattern.findall(text)[0]

    url = "https://passport.ustc.edu.cn/login"
    response = await session.post(
        url=url,
        headers=cas_login_headers,
        data=cas_login_data(lt),
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


async def update_lectures(session: aiohttp.ClientSession, course_list: [Course]) -> [Course]:
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
        course = [course for course in course_list if course.id == schedule_json["lessonId"]][0]

        date = raw_date_to_unix_timestamp(schedule_json["date"])
        startHHMM = int(schedule_json["startTime"])
        endHHMM = int(schedule_json["endTime"])

        startDate = date + int(startHHMM // 100) * 3600 + int(startHHMM % 100) * 60
        endDate = date + int(endHHMM // 100) * 3600 + int(endHHMM % 100) * 60

        location = schedule_json["room"]["nameZh"] if schedule_json["room"] else schedule_json["customPlace"]

        lecture = Lecture(
            startDate=startDate,
            endDate=endDate,
            name=course.name,
            location=location,
            teacherName=schedule_json["personName"],
            periods=schedule_json["periods"],
            additionalInfo={}
        )

        for course in course_list:
            if course.id == schedule_json["lessonId"]:
                course.lectures.append(lecture)
                break

    return course_list
