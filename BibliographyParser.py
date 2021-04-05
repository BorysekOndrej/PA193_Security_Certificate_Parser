import re
from typing import List, Dict

class BibliographyParser:
    def __init__(self):
        self.globalPattern = re.compile(r"(\[([^\s]*)\])[^\S\n]{2,}([\s\S]*?(?=\n{2,}|\n[^\S\n]*\n|\[))")
        self.postprocessPattern = re.compile(r"\s+")
        self.symbolsToSkip = 0.65

    def preprocess(self, input_lines: List[str]):
        text = " ".join(input_lines)
        offset = int(len(text) * self.symbolsToSkip)
        subtext = text[offset:]
        return subtext

    def postprocess(self, string: str):
        return re.sub(self.postprocessPattern, ' ', string).rstrip()

    def parse(self, input_lines: List[str]):
        result: Dict[str, str] = {}
        text = self.preprocess(input_lines)
        bibliography = re.findall(self.globalPattern, text)
        for b in bibliography:
            processed = self.postprocess(b[2])
            result[b[0]] = processed
        return result