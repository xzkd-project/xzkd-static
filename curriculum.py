import asyncio
import os

import aiohttp
from tqdm import tqdm

from utils.catalog import get_semester_list, get_course_list
from utils.jw import login as jw_login, get_course_info
from utils.tools import save_json

def setup():
    global curriculum_dir
    # create "$(base_dir)/build/curriculum" directory if not exists
    base_dir = os.path.dirname(os.path.abspath(__file__))
    curriculum_dir = os.path.join(base_dir, "build", "curriculum")
    if not os.path.exists(curriculum_dir):
        os.mkdir(curriculum_dir)


async def fetch_semester(semester_id: str, session: aiohttp.ClientSession):
    async def fetch_course_info(course_id_chunk: list[str]):
        async with sem:
            course_info = await get_course_info(session, course_id_chunk)

            for course in course_info:
                course_id = course["id"]
                save_json(course, os.path.join(curriculum_dir, semester_id, f"{course_id}.json"))

            pbar.update(len(course_id_chunk))

    if not os.path.exists(os.path.join(curriculum_dir, semester_id)):
        os.mkdir(os.path.join(curriculum_dir, semester_id))

    course_list = await get_course_list(semester_id)
    save_json(course_list, os.path.join(curriculum_dir, semester_id, "course_list.json"))

    # split course_list into chunks of 50
    course_id_list = [str(course["id"]) for course in course_list]
    course_id_chunks = [course_id_list[i:i + 50] for i in range(0, len(course_id_list), 50)]

    sem = asyncio.Semaphore(50)
    pbar = tqdm(total=len(course_id_list))

    tasks = [fetch_course_info(course_id_chunk) for course_id_chunk in course_id_chunks]
    with pbar:
        await asyncio.gather(*tasks)


async def make_curriculum():
    async with aiohttp.ClientSession() as session:
        await jw_login(session)

        semester_list = await get_semester_list()
        save_json(semester_list, os.path.join(curriculum_dir, "semester_list.json"))

        for semester in tqdm(semester_list):
            await fetch_semester(str(semester["id"]), session)


def main():
    setup()
    asyncio.run(make_curriculum())
