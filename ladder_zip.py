# Script for creating Ladder Manager compatible Zip archives.

import argparse
import os
import sys

sys.path.insert(1, "sharpy-sc2")
sys.path.insert(1, os.path.join("sharpy-sc2", "python-sc2"))

from bot_loader import LadderZip
# import sub_module  # Important, do not remove!
from version import update_version_txt

root_dir = os.path.dirname(os.path.abspath(__file__))

# Files or folders common to all bots.
common = [
    (os.path.join("sharpy-sc2", "jsonpickle"), "jsonpickle"),
    (os.path.join("sharpy-sc2", "sharpy"), "sharpy"),
    (os.path.join("sharpy-sc2", "python-sc2", "sc2"), "sc2"),
    (os.path.join("sharpy-sc2", "sc2pathlib"), "sc2pathlib"),
    (os.path.join("sharpy-sc2", "config.py"), "config.py"),
    (os.path.join("sharpy-sc2", "ladder.py"), "ladder.py"),
    ("requirements.txt", None),
    ("version.txt", None),
    ("config.ini", None),
    ("ladderbots.json", None),
]

# Files or folders to be ignored from the archive.
ignored = [
    "__pycache__",
]

ladder_zip = LadderZip(
    "Chance", "Random", [
        ("chance", None),
        (os.path.join("bossman-sc2", "bossman"), "bossman"),
        (os.path.join("queens-sc2", "queens_sc2"), "queens_sc2"),
        ("run.py", None),
        (os.path.join("SC2MapAnalysis", "MapAnalyzer"), "MapAnalyzer"),
    ], common
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
