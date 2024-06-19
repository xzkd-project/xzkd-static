import os
import shutil

from curriculum import main as make_curriculum
from rss import main as make_rss

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(base_dir, "build")

    if not os.path.exists(build_dir):
        os.mkdir(build_dir)

    # ./static -> ./build/*
    static_dir = os.path.join(base_dir, "static")
    shutil.copytree(static_dir, build_dir, dirs_exist_ok=True)

    # ./build/rss
    make_rss()

    # ./build/curriculum
    make_curriculum()
