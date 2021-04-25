import re
from typing import List, Dict, Tuple

from PropertyParserInterface import PropertyParserInterface


class RevisionsParser(PropertyParserInterface):
    def __init__(self, lines: List[str]):
        super().__init__(lines)
        # Pattern to detect date in any format
        self.datePattern = re.compile(r"[0-9]{2,4}[\/\-\.]([0-9]{2}|[A-Za-z]+)[\/\-\.][0-9]{2,4}")
        # Pattern to detect possible two columns in one line
        self.twoColumns = re.compile(r"^[ ]{0,5}(\S+(?:(?!\s{2}).)+)[\s]{3,}(\S+(?:(?!\s{2}).)+)$")

    def find_keywords(self, lines: List[str], keywords: List[str]) -> list:
        subs = [string.lower() for string in keywords]
        # Find line indexes where the substring is
        start_idxs = [i for i, line in enumerate(lines) if any(map(line.lower().__contains__, subs))]
        return start_idxs

#TODO: fix syntax, add return types
    def get_date(self, line: str):
        res = [m for m in re.finditer(pattern, line)]
        # Usually string should contain only one date
        # TODO: add support for no date.
        index = res[0].start(0)
        date_str = res[0].group(0)
        return date_str, index

    def is_table_header(self, string: str, keywords: List[str]):
        """ Check line if it can be a table header """
        score = 0
        columns = re.split(r" {2,}", string)
        if len(columns) > 4 or len(columns) < 2:
            return False
        # Check if does not contain numbers or symbols
        is_alpha_or_space = all(c.isalpha() or c.isspace() for c in string)
        if not is_alpha_or_space: return False 
        # Keywords score TODO: add some logic for scoring
        #[score := score + 1 for keyword in keywords if(keyword in string2)]
        return True

    def extract_formatting_params(self, line: str) -> List[int]:
        """ Tries to extract start indexes for each column """
        # Split line by two or more spaces
        columns = re.split(r" {2,}", line)
        # We need to find index of each column in string.
        # As split does not give indexes, let's try to find by first occurence
        indexes = [line.find(column) for column in columns]
        return indexes

    def extract_two_column_table(self, lines: List[str]):
        """ Tries to extract two-column table """
        table_header_keywords = ['Date', 'Description', 'Rev', 'Revision', 'Version']
        table_header = []
        table_header_found = False
        column1_start_ids = []
        column2_start_ids = []
        table = []
        # TODO: work more with false lines
        false_lines = 0
        final_lines = 0
        for line in lines:
            result = re.findall(self.twoColumns, line)
            if false_lines > 5: return []
            if len(table) > 0:
                if line == '\n':
                    final_lines += 1
                else:
                    final_lines = 0
            if len(result) == 0:
                false_lines += 1
                continue
            # TODO: work more with header. What if no header? 
            if not table_header_found and self.is_table_header(line, table_header_keywords):
                columns = re.split(r" {2,}", line)
                if len(columns) == 2:
                    table_header = columns
                    table_header_found = True
                    # find start indexes of headers
                    #ids = self.extract_formatting_params(line)
                    #column1_start_ids.append(ids[0])
                    #column2_start_ids.append(ids[1])
                continue

            table.append(line)
            

            

    def find_table(self, start: List[int], lines: List[str]):
        for id in start:
            # We take next line after found keyword
            next_line = id + 1
            self.extract_two_column_table(lines[next_line:])


    def parse(self) -> List[dict]:
        keywords = ['Revision History', 'Version Control']
        indexes = self.find_keywords(self.lines, keywords)
        self.find_table(indexes, self.lines)
        return []
