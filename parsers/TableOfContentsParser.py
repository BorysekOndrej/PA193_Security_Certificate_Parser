import re
from typing import List, Dict, Tuple
from pprint import pprint
from loguru import logger

from PropertyParserInterface import PropertyParserInterface


class TableOfContentsParser(PropertyParserInterface):
    def __init__(self, lines: List[str]):
        self.toc_page_num_sep = "....."
        super().__init__(lines)

    @staticmethod
    def __remove_empty_strings_from_arr(a: List[str]) -> List[str]:
        b = list(filter(lambda x: len(x), a))
        b = list(map(lambda x: x.strip(), b))
        return b

    @staticmethod
    def __try_to_split_after_dot_space(a: str) -> List[str]:
        b = a.split(". ", 1)
        b = TableOfContentsParser.__remove_empty_strings_from_arr(b)
        if len(b) == 2:
            # print(b)
            return [b[0], b[1]]
        return [a]

    @staticmethod
    def __extract_number_at_the_start(a: str) -> int:
        try:
            b = a.split(" ", 1)
            return int(b[0])
        except ValueError as e:
            # logger.warning(a)
            return -1

    @staticmethod
    def __two_column_format_align_check(line: str) -> Tuple[int, int, int]:
        dots_sep = "....."  # todo: This has to match the internal attribute of the class
        space_sep = "    "

        dots1 = line.find(dots_sep)
        space1 = line.find(space_sep, dots1 + 2)
        dots2 = line.find(dots_sep, space1 + 2)
        return dots1, space1, dots2

    @staticmethod
    def __check_for_two_columns(a: List[str]) -> bool:
        suspected_two_columns = 0

        for line in a:
            dots1, space1, dots2 = TableOfContentsParser.__two_column_format_align_check(line)
            if dots1 == -1 or space1 == -1 or dots2 == -1:
                continue
            suspected_two_columns += 1

        if suspected_two_columns == 0:
            return False

        # logger.debug(f"{suspected_two_columns} | {len(a)} | {suspected_two_columns*100/len(a)}")
        return True

    @staticmethod
    def __filter_by_magic_sep(a: List[str], sep: str) -> List[str]:

        new_lines = list(filter(lambda x: sep in x, a))
        # logger.warning(f"Lines filtered to {len(new_lines)} lines")
        return new_lines

    @staticmethod
    def __decolumn_lines(lines: List[str]) -> List[str]:
        new_lines = []

        if not TableOfContentsParser.__check_for_two_columns(lines):
            logger.warning("Calling __decolumn_lines on something that doesn't look like two columns")

        for line in lines:
            dots1, space1, dots2 = TableOfContentsParser.__two_column_format_align_check(line)
            if space1 == -1:
                new_lines.append(line)
                continue
            new_lines.append(line[:space1].strip())
            new_lines.append(line[space1:].strip())
            # print(line[space1:].strip())

        return new_lines

    @staticmethod
    def parser1(lines: List[str], sep: str) -> List[Tuple[str, str, int]]:
        answer2 = []

        for single_line in lines:
            b = single_line.split(sep)
            c = TableOfContentsParser.__remove_empty_strings_from_arr(b)
            # logger.info(c)

            if len(c):
                c[-1] = c[-1].lstrip(".").lstrip()

            if len(c) != 2:
                continue

            split1 = list(filter(lambda x: len(x), c[0].split("  ")))
            if len(split1) == 2:
                index_part, name_part = split1[0].strip(), split1[1].strip()
            else:
                index_part, name_part = split1[0], split1[0]

            page_number = TableOfContentsParser.__extract_number_at_the_start(c[1])
            try:
                res_attempt_to_split_name2 = TableOfContentsParser.__try_to_split_after_dot_space(index_part)
                if len(res_attempt_to_split_name2) == 2:
                    index_part, name_part = res_attempt_to_split_name2
                answer2.append((index_part, name_part, page_number))
            except ValueError as e:
                print(c[1])
                pass

        return answer2

    @staticmethod
    def filter_lines_by_num_wildcard_num(lines: List[str], sep: str) -> List[str]:
        new_lines = []
        for line in lines:
            new_line = line.strip()
            if len(new_line) < 2:
                continue
            if not (new_line[0].isnumeric() and new_line[-1].isnumeric()):
                continue
            new_line = new_line.replace(". . ", sep).replace(". .", sep)
            # print(new_line)
            new_lines.append(new_line)

        return new_lines

    @staticmethod
    def parser2(lines: List[str]) -> List[Tuple[str, str, int]]:
        answer = []

        for line in lines:
            try:
                identificator, rest = line.split(" ", 1)
                name, page = rest.rsplit(" ", 1)
                answer.append((identificator.strip(), name.strip(), page.strip()))
            except ValueError as e:
                logger.debug("Split failed")
        return answer

    def get_page_count(self) -> int:
        page_break_char = ""
        return sum(map(lambda x: page_break_char in x, self.lines))

    def filter_results_by_page_numbers(self, a: List[Tuple[str, str, int]]) -> List[Tuple[str, str, int]]:
        page_min = 1
        page_max = self.get_page_count() + 1

        # loguru.debug(page_max)

        try:
            return list(filter(lambda x: page_min <= int(x[2]) <= page_max, a))
        except ValueError as e:
            logger.warning("Filter error - most likely non int in page number")
        return a


    def preprocess(self, lines: List[str]) -> List[str]:
        toc_lines_magic_sep = self.__filter_by_magic_sep(lines, self.toc_page_num_sep)
        toc_lines_num_wildcard_num = self.filter_lines_by_num_wildcard_num(lines, self.toc_page_num_sep)

        toc_lines = toc_lines_magic_sep
        if len(toc_lines_magic_sep) < len(toc_lines_num_wildcard_num):
            toc_lines = toc_lines_num_wildcard_num

        toc_lines = list(filter(lambda x: " " in x, toc_lines))

        # The following line does not improve the results, but does improve the readability of the intermediate results.
        for i in range(30):
            toc_lines = list(map(lambda x: x.replace(self.toc_page_num_sep + ".....", self.toc_page_num_sep), toc_lines))
            toc_lines = list(map(lambda x: x.replace(self.toc_page_num_sep + ".", self.toc_page_num_sep), toc_lines))

        if len(toc_lines) == 0:
            logger.warning(f"Zero ToC lines find after trying all line filter approaches")
            return []

        if self.__check_for_two_columns(toc_lines):
            # logger.warning("This report has probably two columns")
            toc_lines = self.__decolumn_lines(toc_lines)

        return toc_lines

    def main_parse(self, toc_lines: List[str]) -> List[Tuple[str, str, int]]:
        parser_result = self.parser1(toc_lines, self.toc_page_num_sep)
        if len(parser_result) == 0:
            parser_result = self.parser2(toc_lines)

        if len(parser_result) == 0:
            logger.warning(f"No ToC tuples extracted from {len(toc_lines)} suspected ToC lines")
            # logger.debug(toc_lines)

        return parser_result

    def post_filter(self, possible_results: List[Tuple[str, str, int]]) -> List[Tuple[str, str, int]]:
        filtered_results = self.filter_results_by_page_numbers(possible_results)
        return filtered_results

    def parse(self) -> List[Tuple[str, str, int]]:
        toc_lines = self.preprocess(self.lines)
        possible_results = self.main_parse(toc_lines)
        filtered_results = self.post_filter(possible_results)
        return filtered_results
