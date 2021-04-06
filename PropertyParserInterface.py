from typing import List


class PropertyParserInterface:
    def __init__(self, lines: List[str]):
        self.lines: List[str] = lines
        self.canon_text: str = PropertyParserInterface.canonize_string("\n".join(lines))
        self.is_parsed: bool = False
        self.result = None

    @staticmethod
    def canonize_string(a: str) -> str:
        a = a.replace("-\n", ""). \
            replace("\n", " ")

        while "  " in a:
            a = a.replace("  ", " ")

        return a

    def parse(self):
        # self.is_parsed = True
        raise NotImplementedError()

    def get_result(self):
        if not self.is_parsed:
            raise RuntimeWarning("Trying to acquire results for parser that has not parsed the content")

