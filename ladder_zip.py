# Script for creating Ladder Manager compatible Zip archives.

import os
import argparse


# import sub_module  # Important, do not remove!
from version import update_version_txt
from bot_loader import LadderZip

root_dir = os.path.dirname(os.path.abspath(__file__))

# Files or folders common to all bots.
common = [
    (os.path.join("sharpy-sc2", "jsonpickle"), "jsonpickle"),
    (os.path.join("sharpy-sc2", "sharpy"), "sharpy"),
    (os.path.join("sharpy-sc2", "python-sc2", "sc2"), "sc2"),
    (os.path.join("sharpy-sc2", "sc2pathlibp"), "sc2pathlibp"),
    ("requirements.txt", None),
    ("version.txt", None),
    (os.path.join("sharpy-sc2", "config.py"), "config.py"),
    ("config.ini", None),
    (os.path.join("sharpy-sc2", "ladder.py"), "ladder.py"),
    ("ladderbots.json", None),
]

# Files or folders to be ignored from the archive.
ignored = [
    "__pycache__",
]

ladder_zip = LadderZip(
    "Chance", "Random", [("chance", None), ("run.py", None)], common
)


def main():
    parser = argparse.ArgumentParser(
        description="Create a Ladder Manager ready zip archive for SC2 AI, AI Arena, Probots, ..."
    )
    parser.add_argument("-e", "--exe", help="Also make executable (Requires pyinstaller)", action="store_true")
    args = parser.parse_args()

    update_version_txt()

    ladder_zip.create_ladder_zip(args.exe)


if __name__ == "__main__":
    main()
