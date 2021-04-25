import re
from typing import List, Dict, Tuple
import pandas as pd

from PropertyParserInterface import PropertyParserInterface


class RevisionsParser(PropertyParserInterface):
    def __init__(self, lines: List[str]):
        super().__init__(lines)
        # Pattern to detect date in any format
        self.datePattern = re.compile(r"^[0-9]{2,4}[\/\-\.]([0-9]{2}|[A-Za-z]+)[\/\-\.][0-9]{2,4}$")
        # Pattern to detect possible two columns in one line. Parametrized to use for 2-4 columns.
        self.columnsPattern = "^[ ]{0,5}((?:\S+(?:(?!\s{2}).)+)(?:[ ]{3,}(?:\S+(?:(?!\s{2}).)+)){%d})$"
        self.versionPattern = re.compile(r"[0-9]+[\.][0-9]+")

    def find_keywords(self, lines: List[str], keywords: List[str]) -> list:
        subs = [string.lower() for string in keywords]
        # Find line indexes where the substring is
        start_idxs = [i for i, line in enumerate(lines) if any(map(line.lower().__contains__, subs))]
        return start_idxs

#TODO: fix syntax, add return types
    def get_date(self, line: str):
        res = [m for m in re.finditer(self.datePattern, line)]
        # Usually string should contain only one date
        # TODO: add support for no date.
        if len(res) > 0:
            index = res[0].start(0)
            date_str = res[0].group(0)
            return date_str, index
        return "", -1

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
        columns = [x for x in re.split("\s{2,}", line) if x]
        # We need to find index of each column in string.
        # As split does not give indexes, let's try to find by first occurence
        indexes = [line.find(column) for column in columns]
        return indexes

    # TODO: maybe move to some utils class?
    def most_frequent(self, List):
        return max(set(List), key = List.count)

    def extract_table(self, lines: List[str], number_of_cols: int, pattern):
        """ Tries to extract two-column table """
        table_header_keywords = ['Date', 'Description', 'Rev', 'Revision', 'Version']
        table_header = prev_line_format = table = []
        table_header_found = False
        false_lines = final_lines = 0
        for line in lines:
            result = re.findall(pattern, line)
            columns = [x for x in re.split(" {2,}", line) if x]
            if false_lines > 4: return []
            if final_lines > 1: break
            if len(table) > 0:
                # Check the newline at the end
                if line == '\n':
                    final_lines += 1
                    # Reset format indexes to avoid false positives in case of new line
                    prev_line_format = []
                    continue
                else:
                    final_lines = 0
                # Adds line to the table if line is part of the previous
                formatting = self.extract_formatting_params(line)
                if len(formatting) == 1 and formatting[0] in prev_line_format:
                    for i, col in enumerate(prev_line_format):
                        if(formatting[0] == col):
                            table[-1][i] += " " + line
                            break
                    continue
            # Filtering inconsistent data or ToC
            if len(result) == 0 or len(re.findall("[\.]{4,}", line)) > 0:
                false_lines += 1
                continue
            # TODO: work more with header. What if no header? 
            if not table_header_found and self.is_table_header(line, table_header_keywords):
                #columns = re.split(r" {2,}", line)
                if len(columns) == number_of_cols:
                    table_header = columns
                    table_header_found = True
                    # Table line cannot exist before header
                    table = []
                continue

            table.append(list(columns))
            # Find start indexes
            prev_line_format = self.extract_formatting_params(line)
            false_lines = 0
        # TODO: make function fully on dataframe
        if table_header_found:
            return pd.DataFrame(table, columns=table_header)
        else:
            return pd.DataFrame(table)

    def find_table(self, start: List[int], lines: List[str]):
        """ Try to find tables """
        possible_tables = []
        for id in start:
            # We take next line after found keyword
            next_line = id + 1
            for i in range(2, 4):
                pattern = re.compile(self.columnsPattern % (i - 1))
                table = self.extract_table(lines[next_line:], i, pattern)
                if len(table) > 0:
                    possible_tables.append(table)
        # TODO: include table score to select better
        best_table = []
        if len(possible_tables) > 0:
            best_table = max(possible_tables, key=len)
        return best_table



    def parse(self) -> List[dict]:
        keywords = ['Revision History', 'Version Control']
        indexes = self.find_keywords(self.lines, keywords)
        table = self.find_table(indexes, self.lines)
        return []
