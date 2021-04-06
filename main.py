from typing import List, Dict, Optional
import json
import utils
import test_our_implementation
from VersionsParser import VersionsParser
from BibliographyParser import BibliographyParser
from TitleParser import TitleParser

from config import OUTPUT_FOLDER


class ParsingResult:
    def __init__(self):
        self.title: str = ""
        self.versions: Dict[str, List[str]] = {}
        self.table_of_contents: List[List[str, str, int]] = []
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


class ParseDocument():
    def __init__(self, input_lines: List[str], correct_solution: Optional[dict] = None):
        self.lines = input_lines
        self.result = ParsingResult()

        # the following attribute might contain information about the correct solution
        self._correct_solution = correct_solution

        self.complete_parse()

    def complete_parse(self):
        versions_parser = VersionsParser(self.lines)
        bibliography_parser = BibliographyParser(self.lines)
        title_parser = TitleParser(self.lines)

        # self.title_parser.inject_correct_solution(self._correct_solution["title"])

        self.result.versions = versions_parser.parse()
        self.result.title = title_parser.parse()
        self.result.bibliography = bibliography_parser.parse()

    def get_results(self) -> ParsingResult:
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
    main()
