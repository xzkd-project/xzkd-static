import asyncio
import os

import aiohttp
from tqdm import tqdm

from models.course import Course

from utils.catalog import get_semesters, get_courses
from utils.jw import login as jw_login
from utils.jw import update_lectures
from utils.tools import save_json


async def fetch_course_info(session: aiohttp.ClientSession, semester_path: str, _courses: list[Course], sem, progress_bar, course_api_path: str):
    async with sem:
        _courses = await update_lectures(session, _courses)

        for _course in _courses:
            save_json(_course, os.path.join(semester_path, f"{_course.id}.json"))
            save_json(_course, os.path.join(course_api_path, f"{_course.id}"))

        progress_bar.update(len(_courses))


async def fetch_semester(session: aiohttp.ClientSession, curriculum_path: str, semester_id: str, course_api_path: str):
    # create "$(base_dir)/build/curriculum/$(semester_id)" directory if not exists
    semester_path = os.path.join(curriculum_path, semester_id)
    if not os.path.exists(semester_path):
        os.mkdir(semester_path)

    courses = await get_courses(semester_id=semester_id)
    save_json(courses, os.path.join(semester_path, "courses.json"))

    # set semaphore to 50, so that only 50 tasks can run concurrently
    sem = asyncio.Semaphore(50)

    # create a progress bar explicitly in async context
    progress_bar = tqdm(total=len(courses), position=0, leave=True, desc=f"Processing semester id={semester_id}")

    # split into chunks of 50 courses, and fetch them concurrently
    course_chunks = [courses[i:i + 50] for i in range(0, len(courses), 50)]
    tasks = [fetch_course_info(session, semester_path, _courses, sem, progress_bar, course_api_path) for _courses in course_chunks]

    with progress_bar:
        await asyncio.gather(*tasks)


async def make_curriculum():
    base_path = os.path.dirname(os.path.abspath(__file__))
    curriculum_path = os.path.join(base_path, "build", "curriculum")
    course_api_path = os.path.join(base_path, "build", "api", "course")
    if not os.path.exists(curriculum_path):
        os.mkdir(curriculum_path)

    if not os.path.exists(course_api_path):
        os.makedirs(course_api_path)

    async with aiohttp.ClientSession() as session:
        await jw_login(session)

        semesters = await get_semesters()
        save_json(semesters, os.path.join(curriculum_path, "semesters.json"))

        for semester in tqdm(semesters, position=1, leave=True, desc="Processing semesters"):
            await fetch_semester(session, curriculum_path, str(semester.id), course_api_path)


def main():
    asyncio.run(make_curriculum())
