import re
from typing import List, Dict, Tuple

from PropertyParserInterface import PropertyParserInterface


class RevisionsParser(PropertyParserInterface):
    def __init__(self, lines: List[str]):
        super().__init__(lines)
        # Pattern to detect date in any format
        self.datePattern = re.compile(r"[0-9]{2,4}[\/\-\.]([0-9]{2}|[A-Za-z]+)[\/\-\.][0-9]{2,4}")

    def find_keywords(self, lines: List[str], keywords: List[str]) -> list:
        subs = [string.lower() for string in keywords]
        # Find line indexes where the substring is
        start_idxs = [i for i, line in enumerate(lines) if any(map(line.lower().__contains__, subs))]
        return start_idxs

    def get_date(self, line: str) -> str, int:
        res = [m for m in re.finditer(pattern, string)]
        # Usually string should contain only one date
        index = res[0].start(0)
        date_str = res[0].group(0)
        return date_str, index

    def find_table(self, start: List[int], lines: List[str]):
        for id in start:
            pass


    def parse(self) -> List[dict]:
        keywords = ['Revision History', 'Version Control']
        indexes = self.find_keywords(self.lines, keywords)
        return []
