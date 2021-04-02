import json
import glob
from typing import List
from pprint import pprint
from os.path import basename
from pathlib import Path

from config import INPUT_FOLDER, OUTPUT_FOLDER


def convert_dict_to_json_string(a: dict) -> str:
    return json.dumps(a, sort_keys=True, indent=4)


def list_input_files() -> List[str]:
    return glob.glob(f"{INPUT_FOLDER}/*.txt")


def input_filename_to_expected_output_filename(input_filename: str) -> str:
    return input_filename[:-4]+'.json' # removes .txt and adds .json


def input_filename_to_our_output_filename(input_filename: str) -> str:
    return f'{OUTPUT_FOLDER}/'+basename(input_filename[:-4]+".json")


def example_of_names():
    a = list_input_files()[0]
    print(a)
    print(input_filename_to_expected_output_filename(a))
    print(input_filename_to_our_output_filename(a))


def mkdir(path: str):
    Path(path).mkdir(parents=True, exist_ok=True)


def load_file(input_filename: str) -> List[str]:
    with open(input_filename, encoding="utf8") as f:
        return f.readlines()


def main():
    example_of_names()
    pass


if __name__ == "__main__":
    main()
