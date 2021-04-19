import re
from typing import List, Dict, Tuple
from pprint import pprint
from loguru import logger

from PropertyParserInterface import PropertyParserInterface


class TableOfContentsParser(PropertyParserInterface):
    def __init__(self, lines: List[str]):
        super().__init__(lines)

    @staticmethod
    def __split_index_name(a: str) -> Tuple[str, str]:
        b = a.split("  ")
        c = list(filter(lambda x: len(x), b))
        if len(c) == 2:
            return c[0].strip(), c[1].strip()
        return a, a

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
            logger.warning(a)
            return -1

    @staticmethod
    def __filter_by_magic_sep(a: List[str], sep: str) -> List[str]:

        new_lines = list(filter(lambda x: sep in x, a))
        logger.warning(f"Lines filtered to {len(new_lines)} lines")
        return new_lines

    def parse(self) -> List[Tuple[str, str, int]]:
        sep = "......."
        toc_lines = self.__filter_by_magic_sep(self.lines, sep)

        if len(toc_lines) == 0:
            return []

        answer2 = []

        for single_line in toc_lines:
            b = single_line.split(sep)
            c = self.__remove_empty_strings_from_arr(b)

            c[-1] = c[-1].lstrip(".").lstrip()

            cur_part = None

            if len(c) == 2:
                index_part, name_part = self.__split_index_name(c[0])
                page_number = self.__extract_number_at_the_start(c[1])
                try:
                    res_attempt_to_split_name2 = self.__try_to_split_after_dot_space(index_part)
                    if len(res_attempt_to_split_name2) == 2:
                        index_part, name_part = res_attempt_to_split_name2
                    cur_part = (index_part, name_part, page_number)
                    # cur_part = (index_part, name_part, int(c[1]))
                    # print(cur_part)
                except ValueError as e:
                    print(c[1])
                    # cur_part = (c[0], c[0], c[1])
                    pass

            if cur_part:
                answer2.append(cur_part)

        # print(answer2)
        return answer2
