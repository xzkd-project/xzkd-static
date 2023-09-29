import os
import shutil

from curriculum import *

if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.abspath(__file__))
    static_dir = os.path.join(base_dir, "static")
    build_dir = os.path.join(base_dir, "build")

    # copy static files to build directory
    if not os.path.exists(build_dir):
        os.mkdir(build_dir)
    shutil.copytree(static_dir, build_dir, dirs_exist_ok=True)

    make_curriculum()
