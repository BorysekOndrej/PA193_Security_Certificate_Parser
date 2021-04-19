import re
from typing import List, Dict, Tuple
from pprint import pprint

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

    def parse(self) -> List[Tuple[str, str, int]]:
        sep = "......."
        answer = list(filter(lambda x: sep in x, self.lines))

        answer2 = []

        for single_line in answer:
            b = single_line.split(sep)
            c = self.__remove_empty_strings_from_arr(b)

            c[-1] = c[-1].lstrip(".").lstrip()

            cur_part = None

            if len(c) == 2:
                index_part, name_part = self.__split_index_name(c[0])
                try:
                    cur_part = (index_part, name_part, int(c[1]))
                    # print(cur_part)
                except ValueError as e:
                    # print(c[1])
                    # cur_part = (c[0], c[0], c[1])
                    pass

            if cur_part:
                answer2.append(cur_part)

        # print(answer2)
        return answer2
