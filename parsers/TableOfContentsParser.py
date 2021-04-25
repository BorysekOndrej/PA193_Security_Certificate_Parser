import random
import re
import string
from typing import List, Dict, Tuple
from pprint import pprint
from loguru import logger

from PropertyParserInterface import PropertyParserInterface


class TableOfContentsParser(PropertyParserInterface):
    def __init__(self, lines: List[str]):
        self.toc_page_num_sep = "....."
        super().__init__(lines)

    @staticmethod
    def __two_column_format_align_check(line: str) -> Tuple[int, int, int]:
        dots_sep = "....."  # todo: This has to match the internal attribute of the class
        space_sep = "    "

        dots1 = line.find(dots_sep)
        space1 = line.find(space_sep, dots1 + 2)
        dots2 = line.find(dots_sep, space1 + 2)
        return dots1, space1, dots2

    @staticmethod
    def __check_for_two_columns(a: List[str]) -> bool:
        suspected_two_columns = 0

        for line in a:
            dots1, space1, dots2 = TableOfContentsParser.__two_column_format_align_check(line)
            if dots1 == -1 or space1 == -1 or dots2 == -1:
                continue
            suspected_two_columns += 1

        if suspected_two_columns == 0:
            return False

        # logger.debug(f"{suspected_two_columns} | {len(a)} | {suspected_two_columns*100/len(a)}")
        return True

    @staticmethod
    def __filter_by_magic_sep(a: List[str], sep: str) -> List[str]:

        new_lines = list(filter(lambda x: sep in x, a))
        # logger.warning(f"Lines filtered to {len(new_lines)} lines")
        return new_lines

    @staticmethod
    def __decolumn_lines(lines: List[str]) -> List[str]:
        new_lines = []

        if not TableOfContentsParser.__check_for_two_columns(lines):
            logger.warning("Calling __decolumn_lines on something that doesn't look like two columns")

        for line in lines:
            dots1, space1, dots2 = TableOfContentsParser.__two_column_format_align_check(line)
            if space1 == -1:
                new_lines.append(line)
                continue
            new_lines.append(line[:space1].strip())
            new_lines.append(line[space1:].strip())
            # print(line[space1:].strip())

        return new_lines

    @staticmethod
    def parser1(lines: List[str], sep: str, require_sep=False) -> List[Tuple[str, str, int]]:
        answer2 = []

        for single_line in lines:
            # logger.warning(single_line)
            if require_sep and sep not in single_line:
                continue
            c = single_line.replace(sep, " ").rsplit(" ", 1)
            c = list(map(lambda x: x.strip(), c))  # Remove all whitechars from components
            c = list(filter(lambda x: len(x), c))  # Keep only components with non zero length

            if len(c) != 2:
                continue

            identificator_and_title, page_number_string = c

            try:
                page_number_int = int(page_number_string)
            except ValueError as e:
                # logger.warning(f"Page number is not int: {page_number_string}")
                continue
                pass

            # logger.warning(identificator_and_title)

            index_part, name_part = identificator_and_title, identificator_and_title

            if "  " in identificator_and_title:
                # Splitting using split(" ", 1) wouldn't work so well, because some of the parsed out parts don't have identificator.
                split1 = list(filter(lambda x: len(x), identificator_and_title.split("  ")))

                if len(split1) == 2:
                    index_part, name_part = split1[0].strip(), split1[1].strip()
                else:
                    index_part, name_part = split1[0], split1[0]
            else:
                split2 = identificator_and_title.rsplit(". ", 1)
                if len(split2) == 2:
                    index_part, name_part = split2[0].strip(), split2[1].strip()

            answer2.append((index_part, name_part, page_number_int))

        return answer2

    @staticmethod
    def parser2(lines: List[str]) -> List[Tuple[str, str, int]]:
        answer = []

        for line in lines:
            try:
                identificator, rest = line.split(" ", 1)
                if identificator.isnumeric() or "." in identificator or len(identificator) < 3:
                    pass
                else:
                    identificator = ""
                    rest = line

                name, page = rest.rsplit(" ", 1)
                try:
                    answer.append((identificator.strip(), name.strip(), int(page.strip())))
                except ValueError as e:
                    # logger.debug("Page is not int")
                    answer.append((identificator.strip(), name.strip(), -1))
                    pass
            except ValueError as e:
                # logger.debug("Split failed")
                pass
        return answer


    @staticmethod
    def filter_lines_by_num_wildcard_num(lines: List[str], sep: str) -> List[str]:
        new_lines = []
        for line in lines:
            new_line = line.strip()
            if len(new_line) < 2:
                continue
            if not (new_line[0].isnumeric() and new_line[-1].isnumeric()):
                continue
            new_line = new_line.replace(". . ", sep).replace(". .", sep)
            # print(new_line)
            new_lines.append(new_line)

        return new_lines

    @staticmethod
    def get_page_break_char():
        return ""

    def get_page_count(self) -> int:
        return sum(map(lambda x: self.get_page_break_char() in x, self.lines))

    def filter_results_by_page_numbers(self, a: List[Tuple[str, str, int]]) -> List[Tuple[str, str, int]]:
        page_min = 1
        page_max = self.get_page_count() + 1

        # loguru.debug(page_max)

        try:
            return list(filter(lambda x: page_min <= int(x[2]) <= page_max, a))
        except ValueError as e:
            # logger.warning("Filter error - most likely non int in page number")
            pass
        return a

    def filter_lines_by_section_keyword(self, lines):
        possible_starts = ["CONTENTS:", "TABLE OF CONTENTS"]

        def get_toc_section_start(lines):
            section_start = -1
            answer = []
            # max_possible_start_len = max(map(lambda x: len(x), possible_starts))
            line_id = 0
            for line in lines:
                line_stripped = line.strip().lower()
                # if len(line_stripped) > max_possible_start_len + 5:
                #     continue
                for single_start in possible_starts:
                    # if line_stripped.startswith(single_start.lower()):
                    if line_stripped.startswith(single_start.lower()):
                        # logger.warning(line_stripped)
                        section_start = line_id
                        break
                if section_start >= 0:
                    break
                line_id += 1
            return section_start

        def get_first_non_empty_non_numeric_ending_line_id(lines, start_line_id):
            for line_id in range(start_line_id, len(lines)):
                line_stripped = lines[line_id].strip().lower()
                if sum(map(lambda x: x.lower() in line_stripped, possible_starts)):
                    continue
                if line_stripped == "contents":
                    continue
                if len(line_stripped) == 0:
                    continue
                if not line_stripped[-1].isnumeric():
                    return line_id
            return -1


        section_start_line_id = get_toc_section_start(lines)
        if section_start_line_id == -1:
            return []
        section_end_line_id = get_first_non_empty_non_numeric_ending_line_id(lines, section_start_line_id + 1)
        if section_end_line_id == -1:
            return []

        # random_filename = f"results/tmp/" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10)) + ".txt"
        # with open(random_filename+".removed_headers_and_footers.txt", "w", encoding="utf8") as f:
        #     f.writelines(self.remove_header_and_footer(lines))


        # with open(random_filename+".raw.txt", "w", encoding="utf8") as f:
        #     f.writelines(lines[section_start_line_id:section_start_line_id+100])

        answer = list(filter(lambda x: len(x.strip()), lines[section_start_line_id+1:section_end_line_id]))
        answer = list(filter(lambda x: x.strip()[-1].isnumeric(), answer))
        answer = list(map(lambda x: x.strip(), answer))

        # with open(random_filename + ".guessed.txt", "w", encoding="utf8") as f:
        #     f.writelines(answer)

        # logger.debug(random_filename)
        return answer

    def remove_header_and_footer(self, lines: List[str]) -> List[str]:

        def count_non_empty_lines_before_and_after(lines: List[str], line_index: int) -> Tuple[int, int]:
            before = 0
            after = 0
            for i in range(line_index, len(lines)):
                if len(lines[i].strip()) == 0:
                    break
                after += 1
            for i in range(line_index, 0, -1):
                if len(lines[i].strip()) == 0:
                    break
                before += 1

            return before, after

        page_breaks = []
        page_break_char = self.get_page_break_char()

        for i in range(len(lines)):
            if page_break_char in lines[i]:
                page_breaks.append(i)

        footer_and_header_ofsets = []
        for i in range(len(page_breaks)-1):
            footer_and_header_ofsets.append(count_non_empty_lines_before_and_after(lines, page_breaks[i]))
        footer_offset_min = min(map(lambda x: x[0], footer_and_header_ofsets))
        # header_offset_min = min(map(lambda x: x[1], footer_and_header_ofsets))
        header_offset_min = 0

        if footer_offset_min > 5:
            footer_offset_min = 0

        # logger.debug((footer_offset_min, header_offset_min))

        cur_row = 0
        answer = []
        for i in range(len(page_breaks) - 1):
            answer += lines[cur_row:max(0, page_breaks[i]-footer_offset_min)]
            cur_row = min(len(lines), page_breaks[i]+header_offset_min)

        answer += lines[cur_row:len(lines)]
        # logger.debug(page_breaks)

        return answer

    def filter_chapters_directly_from_text(self, lines: List[str]) -> List[str]:
        # This approach is not viable, because it also extracts numerical lists
        answer = []
        for line in lines:
            line_stripped = line.strip()
            if len(line_stripped) == 0:
                continue
            if not line_stripped[0].isnumeric():
                continue
            if "." not in line_stripped:
                continue
            answer.append(line_stripped+"\n")

        random_filename = f"results/tmp/" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10)) + ".txt"
        with open(random_filename, "w", encoding="utf8") as f:
            f.writelines(answer)

        return answer


    def preprocess(self, lines: List[str]) -> List[str]:

        self.filter_chapters_directly_from_text(lines)

        # lines = self.remove_header_and_footer(lines)

        toc_lines_magic_sep = self.__filter_by_magic_sep(lines, self.toc_page_num_sep)
        toc_lines_num_wildcard_num = self.filter_lines_by_num_wildcard_num(lines, self.toc_page_num_sep)
        toc_lines_start_section_by_keyword = self.filter_lines_by_section_keyword(lines)

        min_line_length = 16
        toc_lines_magic_sep = list(filter(lambda x: len(x) >= min_line_length, toc_lines_magic_sep))
        toc_lines_num_wildcard_num = list(filter(lambda x: len(x) >= min_line_length, toc_lines_num_wildcard_num))
        toc_lines_start_section_by_keyword = list(filter(lambda x: len(x) >= min_line_length, toc_lines_start_section_by_keyword))

        toc_lines = toc_lines_magic_sep
        used_approach = "MAGIC_SEP"

        if len(toc_lines) < len(toc_lines_num_wildcard_num):
            used_approach = "NUM WILDCARD"
            toc_lines = toc_lines_num_wildcard_num

        if len(toc_lines) < len(toc_lines_start_section_by_keyword):
            used_approach = "KEYWORD"
            # logger.debug(toc_lines)
            # logger.debug(toc_lines_start_section_by_keyword)
            toc_lines = toc_lines_start_section_by_keyword

        logger.error(used_approach)

        # logger.debug(
        #     f"ToC line lengths {len(toc_lines_magic_sep)} {len(toc_lines_num_wildcard_num)} {len(toc_lines_start_section_by_keyword)}")

        # logger.debug(toc_lines_num_wildcard_num)
        # logger.debug(toc_lines_start_section_by_keyword)

        toc_lines = list(filter(lambda x: " " in x, toc_lines))

        # The following line does not improve the results, but does improve the readability of the intermediate results.
        for i in range(30):
            toc_lines = list(map(lambda x: x.replace(self.toc_page_num_sep + ".....", self.toc_page_num_sep), toc_lines))
            toc_lines = list(map(lambda x: x.replace(self.toc_page_num_sep + ".", self.toc_page_num_sep), toc_lines))

        if len(toc_lines) == 0:
            logger.warning(f"Zero ToC lines find after trying all line filter approaches")
            return []

        if self.__check_for_two_columns(toc_lines):
            # logger.warning("This report has probably two columns")
            toc_lines = self.__decolumn_lines(toc_lines)

        # logger.debug(toc_lines)

        return toc_lines

    def main_parse(self, toc_lines: List[str]) -> List[Tuple[str, str, int]]:
        if len(toc_lines) == 0:
            return []

        parser_results = []
        parser_results.append( self.parser1(toc_lines, self.toc_page_num_sep, require_sep=True) )
        # parser_results.append( self.parser1(toc_lines, self.toc_page_num_sep, require_sep=False) )
        parser_results.append( self.parser2(toc_lines) )
        # logger.debug(list(map(lambda x: len(x), parser_results)))

        for single_result in parser_results:
            if len(single_result) > 0:
                return single_result

        logger.warning(f"No ToC tuples extracted from {len(toc_lines)} suspected ToC lines")
        # logger.debug(toc_lines)
        return []

    def post_filters_and_maps(self, possible_results: List[Tuple[str, str, int]]) -> List[Tuple[str, str, int]]:
        filtered_results = self.filter_results_by_page_numbers(possible_results)
        filtered_results = list(filter(lambda x: not x[0].startswith("Tab. "), filtered_results))
        filtered_results = list(filter(lambda x: not x[0].startswith("Fig. "), filtered_results))
        # filtered_results = list(filter(lambda x: x[0][0].isnumeric(), filtered_results)) # We also want thing labeled with letters.
        filtered_results = list(map(lambda x: (x[0].rstrip("."), x[1], x[2]), filtered_results)) # Remove trailing dot from chapter identifiers
        filtered_results = sorted(filtered_results, key=lambda x: x[2]) # Sort by page. Sorted is guaranteed to be stable.

        return filtered_results

    def parse(self) -> List[Tuple[str, str, int]]:
        toc_lines = self.preprocess(self.lines)
        possible_results = self.main_parse(toc_lines)
        filtered_results = self.post_filters_and_maps(possible_results)
        return filtered_results
