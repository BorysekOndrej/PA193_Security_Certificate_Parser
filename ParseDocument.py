from typing import List, Dict, Optional, Tuple
import json
from loguru import logger
import sys

import utils

import test_our_implementation

from parsers.VersionsParser import VersionsParser
from parsers.BibliographyParser import BibliographyParser
from parsers.TitleParser import TitleParser
from parsers.TableOfContentsParser import TableOfContentsParser
from parsers.RevisionsParser import RevisionsParser

from config import OUTPUT_FOLDER, INJECT_CORRECT_SOLUTION, LOG_LEVEL


class ParsingResult:
    def __init__(self):
        self.title: str = ""
        self.versions: Dict[str, List[str]] = {}
        self.table_of_contents: List[Tuple[str, str, int]] = []
        self.revisions: List[dict] = []
        self.bibliography: Dict[str, str] = {}
        self.other: Dict[str, str] = {}
    
    def make_dict(self) -> dict:
        return {
            "title": self.title,
            "versions": self.versions,
            "table_of_contents": self.table_of_contents,
            "revisions": self.revisions,
            "bibliography": self.bibliography,
            "other": self.other,
        }

    def make_json(self) -> str:
        return utils.convert_dict_to_json_string(self.make_dict())


class ParseDocument:
    def __init__(self, input_lines: List[str], correct_solution: Optional[dict] = None):
        self.lines = input_lines
        self.result = ParsingResult()
        self.complete_parse_started = False

        self.parsers = {
            'title': TitleParser,
            'versions': VersionsParser,
            'table_of_contents': TableOfContentsParser,
            'revisions': RevisionsParser,
            'bibliography': BibliographyParser,
        }

        # the following attribute might contain information about the correct solution
        self._correct_solution = correct_solution

    def complete_parse(self):
        self.complete_parse_started = True
        for field_name in self.parsers:
            parser_instance = self.parsers[field_name](self.lines)

            if INJECT_CORRECT_SOLUTION:
                try:
                    parser_instance.inject_correct_solution(getattr(self._correct_solution, field_name))
                except:
                    pass

            setattr(self.result, field_name, parser_instance.parse())

    def get_results(self) -> ParsingResult:
        if not self.complete_parse_started:
            self.complete_parse()
        return self.result


def main():
    utils.mkdir(OUTPUT_FOLDER)

    for input_filename in utils.list_input_files():
        lines = utils.load_file(input_filename)

        correct_json_dict = json.loads(" ".join(
            utils.load_file(utils.input_filename_to_expected_output_filename(input_filename))
        ))
        pd = ParseDocument(lines, correct_solution=correct_json_dict)
        parsing_result: ParsingResult = pd.get_results()
        
        with open(utils.input_filename_to_our_output_filename(input_filename), "w", encoding="utf8") as f:
            f.write(parsing_result.make_json())
    
    test_our_implementation.main()


if __name__ == "__main__":
    logger.remove()
    logger.add(sys.stderr, level=LOG_LEVEL)
    main()
