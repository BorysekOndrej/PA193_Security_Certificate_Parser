import json
import os

from loguru import logger
import sys
import argparse
from typing import Tuple, List, Optional

import test_our_implementation
import utils
from ParseDocument import ParseDocument, ParsingResult


def cli_entrypoint():
    filename_tuples = process_cli_arguments()

    check_folders_existance(filename_tuples, create_non_existent_folders=True)

    logger.debug(filename_tuples)

    number_of_correct_files_to_inject = sum(map(lambda x: bool(x[2]), filename_tuples))
    if number_of_correct_files_to_inject:
        logger.debug("There are some files with correct output, that will be injected to the parsers. This should only be used during development.")

    evaluate_files(filename_tuples)
    run_official_scorer(filename_tuples)


def process_cli_arguments() -> List[Tuple[str, str, Optional[str]]]:
    log_level = "INFO"

    parser = argparse.ArgumentParser(description='Parse certificates from txt to structured JSON.')

    parser.add_argument('-i', '--input_file', help='A single input TXT file which should be parsed.')
    parser.add_argument('-o', '--output_file', help='A single output JSON file to which the output should be placed.')
    parser.add_argument('--correct_file',
                        help='Debug only: Path to a JSON file with the expected/correct JSON.')

    parser.add_argument('-I', '--input_folder', help='Input folder in which to search for txt files.')
    parser.add_argument('-O', '--output_folder', help='Output folder to which should be outputted our JSONs.')
    parser.add_argument('--correct_folder',
                        help='Debug only: Path to folder which contains the expected/correct JSONs.')

    parser.add_argument('--log_level', default=log_level, help='What Log level to use for the err output. (TRACE, DEBUG, INFO, SUCCESS, WARNING, ERROR, CRITICAL)')
    args = parser.parse_args()

    logger.remove()
    logger.add(sys.stderr, level=args.log_level)

    some_file_flag = args.input_file or args.output_file or args.correct_file
    some_folder_flag = args.input_folder or args.output_folder or args.correct_folder

    if not some_file_flag and not some_folder_flag:
        logger.error("You need to set either file or folder mode.")
        parser.print_help()
        sys.exit(1)

    if some_file_flag and some_folder_flag:
        logger.error("Modes for files and folder are mutually exclusive. Use one or the other. Use one or the other.")
        sys.exit(1)

    if some_file_flag:
        return file_flags_parsing(args)

    if some_folder_flag:
        return folder_flags_parsing(args)

    logger.error("This should be unreachable. If you see this message, most likely a new extension was not implemented correctly.")
    return []


def file_flags_parsing(args) -> List[Tuple[str, str, Optional[str]]]:
    input_file, output_file, correct_file = args.input_file, args.output_file, args.correct_file
    if input_file is None:
        logger.error("Specify the input file")
        sys.exit(1)
    if not output_file:
        output_file = utils.filename_remove_extension(input_file)+".json"
    return [(input_file, output_file, correct_file)]


def folder_flags_parsing(args) -> List[Tuple[str, str, Optional[str]]]:
    # todo: check for trailing slash
    input_folder, output_folder, correct_folder = args.input_folder, args.output_folder, args.correct_folder
    if input_folder is None:
        logger.error("Specify the input folder")
        sys.exit(1)
    if not output_folder:
        output_folder = input_folder

    files: List[str] = []
    try:
        files = utils.list_input_files(input_folder)
    except Exception as e:
        logger.error("Todo: check how can i invoke this exception")
        sys.exit(1)

    answer: List[Tuple[str, str, Optional[str]]] = []

    for single_filename in files:
        filename_segment = utils.filename_from_path(single_filename)

        output_filename_segment = utils.filename_remove_extension(filename_segment)
        if input_folder == output_folder:
            output_filename_segment += ".out"
        output_filename_segment += ".json"
        output_filename = os.path.join(output_folder, output_filename_segment)

        correct_filename = None
        if correct_folder:
            correct_filename_segment = utils.filename_remove_extension(filename_segment) + ".json"
            correct_filename = os.path.join(correct_folder, correct_filename_segment)

        answer.append((single_filename, output_filename, correct_filename))

    return answer


def check_folders_existance(filename_tuples: List[Tuple[str, str, Optional[str]]], create_non_existent_folders=False):
    unique_folder = set()
    for x in filename_tuples:
        output_filename_path = x[1]
        output_folder_path = os.path.dirname(output_filename_path)
        unique_folder.add(output_folder_path)

    for x in unique_folder:
        if not os.path.isdir(x):
            logger.error(f"One of the output folders, doesn't exist: {x}")
            if create_non_existent_folders:
                logger.debug("Trying to create the output folder")
                utils.mkdir(x)


def evaluate_files(filename_tuples: List[Tuple[str, str, Optional[str]]]) -> None:
    for single_file_tuple in filename_tuples:
        logger.debug(single_file_tuple)
        input_filename, output_filename, correct_filename = single_file_tuple

        try:
            lines = utils.load_file(input_filename)
        except FileNotFoundError:
            logger.warning(f"The input file {input_filename} does not exist. Skipping it's evaluation.")
            continue

        correct_json_dict = None
        if correct_filename:
            try:
                correct_json_dict = json.loads(" ".join(utils.load_file(correct_filename)))
            except FileNotFoundError:
                logger.warning(f"The supposedly correct file {correct_filename} does not exist. Evaluationg the input file {input_filename} without it.")

        try:
            pd = ParseDocument(lines, correct_solution=correct_json_dict)
            parsing_result: ParsingResult = pd.get_results()
        except Exception as e:
            logger.error(f"Exception seen during from parsers on file {input_filename}. Skipping this file. (exception: {e})")
            continue

        try:
            with open(output_filename, "w", encoding="utf8") as f:
                f.write(parsing_result.make_json())
        except FileNotFoundError as e:
            # utils.mkdir(OUTPUT_FOLDER) # todo: consider making that DIR
            logger.error(
                f"Exception seen during write to file {output_filename} for input file {input_filename}. Most likely the folder structure is incorrect.")
            continue
        except Exception as e:
            logger.error(
                f"Exception seen during write to file {output_filename} , the result of input file {input_filename}. (exception: {e})")
            continue


def run_official_scorer(filename_tuples: List[Tuple[str, str, Optional[str]]]) -> None:
    try:
        only_correctable_ones = list(filter(lambda x: x[2], filename_tuples))
        if len(only_correctable_ones) != len(filename_tuples):
            logger.info("Not all outputs have their expected output counterparts. Only those that do will be scored by the official tester.")
        test_our_implementation.main(only_correctable_ones)
    except Exception as e:
        logger.error(f"Attempt at scoring failed. Skipping it. (exception: {e})")


if __name__ == "__main__":
    cli_entrypoint()
