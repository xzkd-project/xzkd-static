import json

import aiohttp

from utils.constants import catalog_headers as headers


async def get_token() -> str:
    url = "https://catalog.ustc.edu.cn/get_token"
    async with aiohttp.ClientSession() as session:
        response = await session.get(
            url=url,
            headers=headers,
            allow_redirects=False
        )
        json = await response.json()
    return json["access_token"]


async def get_semester_list() -> json:
    token = await get_token()
    url = "https://catalog.ustc.edu.cn/api/teach/semester/list?access_token=" + token
    async with aiohttp.ClientSession() as session:
        response = await session.get(
            url=url,
            headers=headers,
            allow_redirects=False
        )
        json = await response.json()
    return json


async def get_course_list(semester_id: str) -> json:
    token = await get_token()
    url = "https://catalog.ustc.edu.cn/api/teach/lesson/list-for-teach/" + semester_id + "?access_token=" + token
    async with aiohttp.ClientSession() as session:
        response = await session.get(
            url=url,
            headers=headers,
            allow_redirects=False
        )
        json = await response.json()
    return json
