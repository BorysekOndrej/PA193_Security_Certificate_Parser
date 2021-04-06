import re
from typing import List, Dict, Tuple

from PropertyParserInterface import PropertyParserInterface


class TableOfContentsParser(PropertyParserInterface):
    def __init__(self, lines: List[str]):
        super().__init__(lines)

    def parse(self) -> List[Tuple[str, str, int]]:
        return []
