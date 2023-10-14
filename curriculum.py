import asyncio
import os

import aiohttp
from tqdm import tqdm

from utils.catalog import get_semesters, get_courses
from utils.jw import login as jw_login, update_lectures
from utils.tools import save_json

from models.course import Course


def setup():
    global curriculum_dir
    # create "$(base_dir)/build/curriculum" directory if not exists
    base_dir = os.path.dirname(os.path.abspath(__file__))
    curriculum_dir = os.path.join(base_dir, "build", "curriculum")
    if not os.path.exists(curriculum_dir):
        os.mkdir(curriculum_dir)


async def fetch_semester(semester_id: str, session: aiohttp.ClientSession):
    async def fetch_course_info(_chunk: [Course]):
        async with sem:
            _chunk = await update_lectures(session, _chunk)

            for _course in _chunk:
                save_json(_course, os.path.join(curriculum_dir, semester_id, f"{_course.id}.json"))

            pbar.update(len(_chunk))

    if not os.path.exists(os.path.join(curriculum_dir, semester_id)):
        os.mkdir(os.path.join(curriculum_dir, semester_id))

    courses = await get_courses(semester_id)
    save_json(courses, os.path.join(curriculum_dir, semester_id, "courses.json"))

    course_chunks = [courses[i:i + 50] for i in range(0, len(courses), 50)]
    sem = asyncio.Semaphore(50)
    pbar = tqdm(total=len(courses))
    tasks = [fetch_course_info(_chunk) for _chunk in course_chunks]
    with pbar:
        await asyncio.gather(*tasks)


async def make_curriculum():
    async with aiohttp.ClientSession() as session:
        await jw_login(session)

        semesters = await get_semesters()
        save_json(semesters, os.path.join(curriculum_dir, "semesters.json"))

        for semester in tqdm(semesters):
            await fetch_semester(str(semester.id), session)


def main():
    setup()
    asyncio.run(make_curriculum())
