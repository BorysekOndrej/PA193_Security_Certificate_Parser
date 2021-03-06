from typing import List, Dict, Optional, Tuple
from loguru import logger

import utils

from parsers.VersionsParser import VersionsParser
from parsers.BibliographyParser import BibliographyParser
from parsers.TitleParser import TitleParser
from parsers.TableOfContentsParser import TableOfContentsParser
from parsers.RevisionsParser import RevisionsParser


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

            if self._correct_solution:
                try:
                    parser_instance.inject_correct_solution(self._correct_solution.get(field_name, None))
                except Exception as e:
                    logger.debug(f"An exception during injection of solution for {field_name}. Continuing the parser without the correct solution. (exception: {e})")

            try:
                setattr(self.result, field_name, parser_instance.parse())
            except Exception as e:
                logger.error(f"An exception escaped parser of {field_name}. Using default empty result instead.")

    def get_results(self) -> ParsingResult:
        if not self.complete_parse_started:
            self.complete_parse()
        return self.result


if __name__ == "__main__":
    logger.warning("This file has an empty main. Use CLI or include it from a different file.")

