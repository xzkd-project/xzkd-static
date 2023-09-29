import requests
import os
import shutil
from tqdm import tqdm

from utils.catalog import *
from utils.jw import *

def save(obj: any, path: str):
    with open(path, "w") as f:
        json.dump(obj, f, indent=4, ensure_ascii=False)

def make_curriculum():
    # create "$(base_dir)/build/curriculum" directory if not exists
    base_dir = os.path.dirname(os.path.abspath(__file__))
    curriculum_dir = os.path.join(base_dir, "build", "curriculum")
    if not os.path.exists(curriculum_dir):
        os.mkdir(curriculum_dir)

    # prepare session
    s = requests.Session()
    jw_login(s)

    # get semester list
    semester_list = get_semester_list()
    save(semester_list, os.path.join(curriculum_dir, "semester_list.json"))

    for semester in tqdm(semester_list):
        # only fetch current semester:
        if semester["isLast"] == False:
            continue

        if not os.path.exists(os.path.join(curriculum_dir, str(semester["id"]))):
            os.mkdir(os.path.join(curriculum_dir, str(semester["id"])))

        semester_id = semester["id"]
        course_list = get_course_list(str(semester_id))
        save(course_list, os.path.join(curriculum_dir, str(semester_id), "course_list.json"))

        for course in tqdm(course_list):
            course_id = course["id"]
            course_info = get_course_info(s, [str(course_id)])
            save(course_info, os.path.join(curriculum_dir, str(semester_id), f"{str(course_id)}.json"))
