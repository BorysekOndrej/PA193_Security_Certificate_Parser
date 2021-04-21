import re
from typing import List, Dict, Tuple

from PropertyParserInterface import PropertyParserInterface


class RevisionsParser(PropertyParserInterface):
    def __init__(self, lines: List[str]):
        super().__init__(lines)

    def find_rev(self, lines: List[str]):
        subs = ['Revision History', 'Version Control']
        subs = [string.lower() for string in subs]
        # Find line indexes where the substring is
        start_idxs = [i for i, line in enumerate(lines) if any(map(line.lower().__contains__, subs))]
        print(start_idxs)



    def parse(self) -> List[dict]:
        self.find_rev(self.lines)
        return []
