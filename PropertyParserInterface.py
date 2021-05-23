from typing import List


class PropertyParserInterface:
    def __init__(self, lines: List[str]):
        self.lines: List[str] = lines
        self.result = None

        # This field might contain correct solution loaded from the dataset. It's here for sanity checks and exploratory
        # analysis, not for help with parsing.
        self._correct_solution = None

    def parse(self):
        raise NotImplementedError()

    @staticmethod
    def canonize_string(a: str) -> str:
        a = a.replace("-\n", ""). \
            replace("\n", " ")

        while "  " in a:
            a = a.replace("  ", " ")

        return a

    def inject_correct_solution(self, correct_solution):
        self._correct_solution = correct_solution

