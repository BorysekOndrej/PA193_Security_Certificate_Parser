import re
from typing import List, Dict, Pattern, Set


class VersionsParser:
    """
    A class for parsing versions of algorithms/components.
    """
    def __init__(self, input_lines: List[str]):
        """
        Initializes the parser to detect versions of specific components from input_lines
        :param input_lines: the lines to look in
        """
        self.lines = input_lines
        self.versions: Dict[str, List[str]] = {}

        self.patterns: Dict[str, Pattern[str]] = {}
        self.patterns["eal"] = re.compile('(?:eal|EAL) ?[0-9]\\+?')
        self.patterns["global_platform"] = re.compile('[Gg]lobal ?[Pp]latform ?(?:\\d\\.)*\\d')
        self.patterns["java_card"] = re.compile('[Jj]ava ?[Cc]ard ?(?:\\d\\.)*\\d')
        self.patterns["sha"] = re.compile('(?:sha|SHA)[ -_]?[0-9]+')
        self.patterns["rsa"] = re.compile('(?:rsa|RSA)[ -_]?[0-9/]{2,}|RSA[^ \\n]*(?:PKCS|PSS)[^ \\n]*')
        self.patterns["ecc"] = re.compile('(?:ecc|ECC)[ -_]?[0-9]+')
        self.patterns["des"] = re.compile('(?:T|3|[Tt]riple)[ -]?DES|DES3')

    def lines_findall(self, pattern: Pattern[str]) -> List[str]:
        """
        Goes through all lines and finds all matches of the pattern
        :param pattern: re.Pattern to look for in the lines
        :return: a list of the matches
        """
        res: Set[str] = set()

        for line in self.lines:
            matched = pattern.findall(line)
            res.update(set(matched))

        return list(res)

    def complete_parse(self) -> None:
        """
        Parse the versions, which can then be retrieved by get_versions
        """
        self.versions = {}

        for key in self.patterns.keys():
            res = self.lines_findall(self.patterns[key])
            if res:
                self.versions[key] = res

    def get_versions(self) -> Dict[str, List[str]]:
        """
        Returns a dict with keys eal, global_platform, java_card, sha, rsa, ecc, des, where the values are lists
        of detected versions of the specific component (some keys may be skipped, if no version was detected).
        complete_parse needs to be called previously

        :return: the dict with the versions
        """
        return self.versions
