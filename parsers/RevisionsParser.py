import re
from typing import List, Dict, Tuple

from PropertyParserInterface import PropertyParserInterface


class RevisionsParser(PropertyParserInterface):
    def __init__(self, lines: List[str]):
        super().__init__(lines)

    def parse(self) -> List[dict]:
        return []
