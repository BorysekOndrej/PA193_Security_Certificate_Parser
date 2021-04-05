import re
from typing import List, Dict, Pattern, Set


class VersionsParser:
    def __init__(self, input_lines: List[str]):
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
        res: Set[str] = set()

        for line in self.lines:
            matched = pattern.findall(line)
            res.update(set(matched))

        return list(res)

    def get_versions(self) -> Dict[str, List[str]]:
        for key in self.patterns.keys():
            res = self.lines_findall(self.patterns[key])
            if res:
                self.versions[key] = res

        return self.versions
