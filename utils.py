import json
import glob
import os
from typing import List
from pprint import pprint
from pathlib import Path


def convert_dict_to_json_string(a: dict) -> str:
    return json.dumps(a, sort_keys=True, indent=4)


def list_input_files(input_folder: str) -> List[str]:
    return glob.glob(f"{input_folder}/*.txt")


def filename_remove_extension(input_filename: str) -> str:
    return os.path.splitext(input_filename)[0]


def filename_from_path(input_filename: str) -> str:
    # warning: be carefull about things ending with /
    # https://docs.python.org/3/library/os.path.html#os.path.basename
    return os.path.basename(input_filename)


def mkdir(path: str):
    Path(path).mkdir(parents=True, exist_ok=True)


def load_file(input_filename: str) -> List[str]:
    with open(input_filename, encoding="utf8") as f:
        return f.readlines()


def load_file_json(input_filename: str) -> dict:
    with open(input_filename, "r", encoding="utf8") as f:
        return json.load(f)


def normalize_json_file(input_filename: str):
    data = load_file_json(input_filename)
    with open(input_filename, "w", encoding="utf8") as f:
        f.write(json.dumps(data, sort_keys=True, indent=4))


def main():
    pass


if __name__ == "__main__":
    main()
