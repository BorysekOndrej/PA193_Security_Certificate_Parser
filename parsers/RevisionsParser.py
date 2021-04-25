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
        self.versionDetectionPattern = re.compile(r"[a-zA-Z\.]{0,10}[0-9]+[\.][0-9]+$")
        self.versionPattern = re.compile(r"([0-9]+[\.][0-9]+)")

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
            for i in range(2, 5):
                pattern = re.compile(self.columnsPattern % (i - 1))
                table = self.extract_table(lines[next_line:], i, pattern)
                if len(table) > 0:
                    possible_tables.append(table)
        # TODO: include table score to select better
        best_table = []
        if len(possible_tables) > 0:
            best_table = max(possible_tables, key=len)
        return best_table

    def process_ver(self, input: str) -> str:
        res = re.findall(self.versionPattern, input)
        if len(res) == 0:
            res = ""
        return res[0]

    def process_desc(self, input: str) -> str:
        return " ".join(input.split())

    # NOT WORKING NOW
    def postprocess(self, table: pd.DataFrame) -> List[dict]:
        """ Remove unwanted spaces and symbols from the revision table """
        # TODO: add table and header emptiness check
        allowed_cols = ['version', 'date', 'description']
        ver_kwords = ['Version', 'Revision', 'Rev']
        date_kwords = ['Date']

        # Here we try to detect types of data
        # col_names = list(table.columns)
        # for i, c in enumerate(col_names):
        #     col_names[i] = c.replace('\n', '')
        # with_alpha_header = all(char.isalpha() or char.isspace() for e in col_names for char in e)
        # if with_alpha_header:
        #     ver_kwords = [x.lower() for x in ver_kwords]
        #     date_kwords = [x.lower() for x in date_kwords]
        #     for i, c in enumerate(col_names):
        #         if any(key in c.lower() for key in ver_kwords):
        #             col_names[i] = 'version'
        #         if any(key in c.lower() for key in date_kwords):
        #             col_names[i] = 'date'
        #     # The last column is always a description        
        #     col_names[-1] = 'description'
        
        #TODO: add detection from data

        for col in list(table.columns):
            date_score = ver_score = other_score = 0
            for i in range(len(table)):
                val = table[col].iloc[i]
                date_match = re.findall(self.datePattern, val)
                if len(date_match) > 0:
                    date_score += 1
                ver_match = re.findall(self.versionDetectionPattern, "".join(val.split()))
                if len(ver_match) > 0:
                    ver_score += 1
            if ver_score > date_score:
                table.rename(columns={col : 'version'}, inplace=True)
            if date_score > ver_score:
                table.rename(columns={col : 'date'}, inplace=True)
        table.columns = [*table.columns[:-1], 'description']
        # remove unused columns
        table = table[table.columns.intersection(allowed_cols)]
        # postprocess data
        table['version'] = table['version'].map(self.process_ver)
        table['description'] = table['description'].map(self.process_desc)
        return table

    def dataframe_to_dict(self, table: pd.DataFrame) -> List[dict]:
        out = []
        for i, row in table.iterrows():
            revision_item = dict()
            if 'version' in table.columns:
                revision_item['version'] = row['version']
            else: revision_item['version'] = ""
            if 'date' in table.columns:
                revision_item['date'] = row['date']
            else: revision_item['date'] = ""
            if 'description' in table.columns:
                revision_item['description'] = row['description']
            else: revision_item['description'] = ""
            out.append(revision_item)
        return out

    def parse(self) -> List[dict]:
        keywords = ['Revision History', 'Version Control']
        indexes = self.find_keywords(self.lines, keywords)
        table = self.find_table(indexes, self.lines)
        if len(table) > 0:
            table = self.postprocess(table)
            return self.dataframe_to_dict(table)
        #print(table)
        
        return []
