from loguru import logger
import sys
import argparse

import config
from ParseDocument import main


def process_cli_arguments():
    parser = argparse.ArgumentParser(description='Parse certificates from txt to structured JSON.')
    parser.add_argument('-I', '--input_folder',
                        default=config.INPUT_FOLDER, help='Input folder in which to search for txt files.')
    # parser.add_argument('--expected_folder',
    #                    default=config.INPUT_FOLDER, help='Debug only: Path to folder which contains the expected/correct JSONs.')
    parser.add_argument('-O', '--output_folder',
                        default=config.OUTPUT_FOLDER, help='Output folder to which should be outputted our JSONs.')
    parser.add_argument('--log_level', default=config.LOG_LEVEL, help='What Log level to use for the err output.')
    args = parser.parse_args()

    config.INPUT_FOLDER = args.input_folder
    config.OUTPUT_FOLDER = args.output_folder
    config.LOG_LEVEL = args.log_level


def cli_entrypoint():
    logger.remove()
    logger.add(sys.stderr, level=config.LOG_LEVEL)
    process_cli_arguments()
    main()


if __name__ == "__main__":
    cli_entrypoint()
