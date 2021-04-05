import re
from typing import List, Dict


class TitleParser:
    """ Title parser"""
    def __init__(self):
        self.max_first_x_lines = 40
        self.input_lines = []
        self.fallback_take_first_n_lines = 5

        self._correct_title = None
        pass

    def __until_first_double_newline(self) -> str:
        """
        The idea was to take first lines until double newline was encoutered. It doesn't work nearly as well as I would have hoped.
        """
        consequiteve_newlines = ""
        for i in range(len(self.input_lines[:self.max_first_x_lines])):
            if consequiteve_newlines == 2:
                return TitleParser.basic_transform(self.__take_first_n_lines(i))
            if len(self.input_lines[i].strip()) == 0:
                consequiteve_newlines += 1
            else:
                consequiteve_newlines = 0
        return self.__fallback()

    def __take_first_n_lines(self, n: int) -> str:
        return " ".join(self.input_lines[:n])

    @staticmethod
    def basic_transform(a: str) -> str:
        a = a.replace("-\n", "").\
            replace("\n", " ")

        to_remove = ["Evaluation documentation", "Final Public", "PUBLIC"]

        for x in to_remove:
            pattern = re.compile(x, re.IGNORECASE)
            a = pattern.sub("", a)

        while "  " in a:
            a = a.replace("  ", " ")
        return a

    def __fallback(self) -> str:
        return self.__take_first_n_lines(self.fallback_take_first_n_lines)

    def check_correct_solution_is_somewhere_in_there(self):
        a = TitleParser.basic_transform("\n".join(self.input_lines[:self.max_first_x_lines]))
        return self._correct_title in a

    def parse(self, input_lines: List[str]) -> str:
        self.input_lines = input_lines


        answer = TitleParser.basic_transform(self.__fallback())
        # print(answer)
        # print(self._correct_title)
        # print()
        return answer

    def add_correct_title(self, correct_title: str):
        self._correct_title = correct_title
