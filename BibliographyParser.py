import re
from typing import List, Dict

class BibliographyParser:
    """ Pibliography parser. Works with list of lines from the text file. """
    def __init__(self):
        """ Initialize the parser, set parsing settings """
        # This bibliography parsing regex works as follows:
        # (\[([^\s]*)\]) group tries to find a left square braket '[' with any character(s) inside the brakets 
        # apart from newline and spaces. This group returns square brakets with value inside. Also you can use 
        # the group inside to get the value from inside the square brakets.
        # The square brakets should be followed by at least two spaces - '[^\S\n]{2,}'. Python does not have \h param.
        # The last regex group - ([\s\S]*?(?=\n{2,}|\n[^\S\n]*\n|\[))") tries to find any sequence of characters 
        # including newline and spaces. But it is limited to two the newline delimiters or empty line -\n[^\S\n]*\n,
        # or just left square braket '['.
        self.globalPattern = re.compile(r"(\[([^\s]*)\])[^\S\n]{2,}([\s\S]*?(?=\n{2,}|\n[^\S\n]*\n|\[))")
        # Removes redundant spaces, tabs and new lines
        self.postprocessPattern = re.compile(r"\s+")
        # We assume that bibliography is always somewhere at the end of the document to have less false positives.
        # This numper is just percent of text where we start. 0.65 means we start searching for the patterns after
        # 65% of text.
        self.symbolsToSkip = 0.65

    def preprocess(self, input_lines: List[str]):
        """ Preprocess input list of strings by concatenation of the lines and taking only predefined % of text."""
        text = " ".join(input_lines)
        offset = int(len(text) * self.symbolsToSkip)
        subtext = text[offset:]
        return subtext

    def postprocess(self, string: str):
        """ Remove all redundant whitespaces and newline characters. """
        return re.sub(self.postprocessPattern, ' ', string).rstrip()

    def parse(self, input_lines: List[str]) -> Dict[str, str]:
        """ Parse input text and find bibliography. """
        result: Dict[str, str] = {}
        text = self.preprocess(input_lines)
        bibliography = re.findall(self.globalPattern, text)
        for b in bibliography:
            # Here we take the third element of the tuple defined by the regex
            processed = self.postprocess(b[2])
            result[b[0]] = processed
        return result
