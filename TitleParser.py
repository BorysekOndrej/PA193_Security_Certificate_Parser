import re
from typing import List, Dict, Tuple


class TitleParser:
    """ Title parser"""
    def __init__(self):
        self.max_first_x_lines = 40
        self.input_lines = []
        self.cannon_string = ""
        self.fallback_take_first_n_lines = 5

        self._correct_title = None
        pass

    def __take_first_n_lines(self, n: int) -> str:
        return " ".join(self.input_lines[:n])

    @staticmethod
    def cannonize_string(a: str) -> str:
        a = a.replace("-\n", ""). \
            replace("\n", " ")

        while "  " in a:
            a = a.replace("  ", " ")
        return a

    @staticmethod
    def basic_transform(a: str) -> str:
        a = TitleParser.cannonize_string(a)
        to_remove = ["Evaluation documentation", "Final Public", "PUBLIC", "Security Target Lite", "Evaluation document"]

        for x in to_remove:
            pattern = re.compile(x, re.IGNORECASE)
            a = pattern.sub("", a)

        while "  " in a:
            a = a.replace("  ", " ")

        a = a.split("Rev. ")[0]

        return a

    def __fallback(self) -> str:
        return self.__take_first_n_lines(self.fallback_take_first_n_lines)

    def check_correct_solution_is_somewhere_in_there(self):
        a = TitleParser.basic_transform("\n".join(self.input_lines[:self.max_first_x_lines]))
        return self._correct_title in a

    def extract_from_template(self, magic_phrase_start: str, magic_phrase_end: str) -> Tuple[str, bool]:
        b = self.cannon_string

        if magic_phrase_start not in b:
            return "", False
        magic_phrase_start_pos = b.find(magic_phrase_start)
        title_start = magic_phrase_start_pos + len(magic_phrase_start)
        title_end = b.find(magic_phrase_end, title_start)
        if title_end == -1 or title_end - title_start > 150:
            title_end = b.find(".", title_start)
        if title_end == -1:
            title_end = title_end + 50
        # print(b[title_start:title_end])
        return b[title_start:title_end], True

    def try_templates(self) -> Tuple[str, bool]:
        templates = [
            ("This Certification Report states the outcome of the Common Criteria security evaluation of the",
             ". The developer"),
            ("The Target of Evaluation (TOE) is called: ",
             " The following table"),
        ]
        for x in templates:
            title, found = self.extract_from_template(x[0], x[1])
            if found:
                return title, True
        return "", False

    def parse(self, input_lines: List[str]) -> str:
        self.input_lines = input_lines
        self.cannon_string = self.cannonize_string("\n".join(self.input_lines))

        # print(self.check_correct_solution_is_somewhere_in_there())

        title, found = self.try_templates()
        if found:
            return title.strip()

        answer = TitleParser.basic_transform(self.__fallback())
        # print(answer)
        # print(self._correct_title)
        # print()
        return answer.strip()

    def add_correct_title(self, correct_title: str):
        self._correct_title = correct_title
