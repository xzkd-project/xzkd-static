import json
import re
import aiohttp

from utils.cas import cas_login_data
from utils.constants import normal_headers as headers
from utils.constants import cas_login_headers


async def login(session: aiohttp.ClientSession):
    url = "https://jw.ustc.edu.cn/"
    response = await session.get(
        url,
        headers=headers,
        allow_redirects=False
    )

    url = "https://jw.ustc.edu.cn/ucas-sso/login"
    response = await session.get(
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


async def get_course_info(session: aiohttp.ClientSession, id_list: list[str]) -> json:
    """
    Notice: login first
    """
    url = "https://jw.ustc.edu.cn/ws/schedule-table/datum"
    data = {
        "lessonIds": id_list,
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
    return json["result"]["lessonList"]
