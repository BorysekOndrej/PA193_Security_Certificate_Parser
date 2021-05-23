import random
import string
from typing import List, Dict, Tuple
from pprint import pprint
from loguru import logger

from PropertyParserInterface import PropertyParserInterface

DOTS_SEP = "....."


class TableOfContentsParser(PropertyParserInterface):
    def __init__(self, lines: List[str]):
        super().__init__(lines)

    def parse(self) -> List[Tuple[str, str, int]]:
        try:
            toc_lines = self.__preprocess_lines(self.lines)
            possible_results = self.__transform_lines_to_tuples(toc_lines)
            filtered_results = self.__post_action_data_cleanup(self.lines, possible_results)
            return filtered_results
        except Exception as e:
            logger.error(f"Uncaught exception from depths of ToC parse. Returning empty ToC. (exception: {e}")
        return []

    @staticmethod
    def __preprocess_lines(lines: List[str]) -> List[str]:
        toc_suspected_lines = {}
        try:
            toc_suspected_lines["MAGIC_SEP"] = list(filter(lambda x: DOTS_SEP in x, lines))
            toc_suspected_lines["NUM_BODY_NUM"] = FilterLinesByNumWildcardNum.filter_lines_by_num_wildcard_num(lines)
            toc_suspected_lines["SECTION_KEYWORD"] = FilterLinesBySectionKeyword.filter_lines_by_section_keyword(lines)
        except Exception as e:
            logger.error(f"Exception inside line preprocessing. Trying to continue with results from other methods. (exception: {e}")

        min_line_length = 16
        for key in toc_suspected_lines:
            toc_suspected_lines[key] = list(filter(lambda x: " " in x, toc_suspected_lines[key]))
            toc_suspected_lines[key] = list(filter(lambda x: len(x) >= min_line_length, toc_suspected_lines[key]))

        logger.debug(
            f"ToC line lengths {[list(map(lambda key: (key, len(toc_suspected_lines[key]) ), toc_suspected_lines))]}")

        toc_lines = []
        used_approach = "NONE"

        for key in toc_suspected_lines:
            if len(toc_lines) < len(toc_suspected_lines[key]):
                toc_lines = toc_suspected_lines[key]
                used_approach = key

        if len(toc_lines) == 0:
            logger.warning(f"Zero ToC lines find after trying all line filter approaches")
            return []

        # logger.debug(used_approach)

        # The following line does not improve the results, but does improve the readability of the intermediate results.
        for i in range(30):
            toc_lines = list(map(lambda x: x.replace(DOTS_SEP + "."*5, DOTS_SEP), toc_lines))  # This is just a way to replace it quicker
            toc_lines = list(map(lambda x: x.replace(DOTS_SEP + ".", DOTS_SEP), toc_lines))

        try:
            toc_lines = DecolumnLines.decolumn_lines(toc_lines)
        except Exception as e:
            logger.error(f"Exception de-column proccess. Trying to continue without the result from it. (exception: {e}")
        # logger.debug(toc_lines)

        toc_lines = list(map(lambda x: x.strip(), toc_lines))  # Remove all whitechars from components
        toc_lines = list(filter(lambda x: len(x), toc_lines))  # Keep only components with non zero length

        return toc_lines

    @staticmethod
    def __transform_lines_to_tuples(toc_lines: List[str]) -> List[Tuple[str, str, int]]:
        if len(toc_lines) == 0:
            return []

        # The parsers here should be ordered by DESC confidence.
        parser_results = []

        try:
            parser_results.append(Parser1.parser1(toc_lines, DOTS_SEP, require_sep=True))
        except Exception as e:
            logger.error(f"Exception from parser1. Trying to continue without the result from it. (exception: {e}")

        try:
            parser_results.append(Parser2.parser2(toc_lines))
        except Exception as e:
            logger.error(f"Exception from parser2. Trying to continue without the result from it. (exception: {e}")

        # logger.debug(list(map(lambda x: len(x), parser_results)))

        for single_result in parser_results:
            if len(single_result) > 3:
                return single_result

        logger.warning(f"No ToC tuples extracted from {len(toc_lines)} suspected ToC lines")
        return []

    @staticmethod
    def __post_action_data_cleanup(all_lines: List[str], possible_results: List[Tuple[str, str, int]]) -> List[Tuple[str, str, int]]:
        if len(possible_results) == 0:
            return []

        forbidden_starts = ["Tab. ", "Fig. ", "Table "]

        filtered_results = possible_results

        page_max = get_page_count(all_lines) + 1
        filtered_results = list(filter(lambda x: 1 <= x[2] <= page_max, filtered_results))

        for single_start in forbidden_starts:
            filtered_results = list(filter(lambda x: not x[0].startswith(single_start), filtered_results))
            filtered_results = list(filter(lambda x: not x[1].startswith(single_start), filtered_results))

        # filtered_results = list(filter(lambda x: x[0].isnumeric(), filtered_results))  # We also want things labeled with letters.
        filtered_results = list(map(lambda x: (x[0].rstrip("."), x[1], x[2]), filtered_results))  # Remove trailing dot from chapter identifiers

        filtered_results = sorted(filtered_results, key=lambda x: x[2])  # Sort by page. Sorted is guaranteed to be stable.

        # Remove multiple spaces
        for i in range(30):
            filtered_results = list(map(lambda x: (x[0], x[1].replace("  ", " "), x[2]), filtered_results))

        return filtered_results


class Parser1:
    """
        This parser to tries to take every line and check, whether it's in one of the following formats format:
            anything  anything number
            anything. anything number
        If both the first number and the last number is correctly parsed, it's added to the result.

        It also has the option to split not on space, but also on custom separator.
        In addition it also allows to prefilter lines based on the presence of the separateror. This is intended to find lines with sep "...." which is common in ToCs.
    """

    @staticmethod
    def parser1(lines: List[str], sep: str, require_sep=False) -> List[Tuple[str, str, int]]:
        answer2 = []

        for single_line in lines:
            # logger.warning(single_line)
            if require_sep and sep not in single_line:
                continue
            c = single_line.replace(sep, " ")
            c = c.rsplit(" ", 1)
            c = list(map(lambda x: x.strip(), c))  # Remove all whitechars from components
            c = list(filter(lambda x: len(x), c))  # Keep only components with non zero length

            if len(c) != 2:
                continue

            identificator_and_title, page_number_string = c

            try:
                page_number_int = int(page_number_string)
            except ValueError as _:
                continue

            # logger.warning(identificator_and_title)

            index_part, name_part = "", identificator_and_title.strip()

            two_spaces = "  "
            if two_spaces in identificator_and_title:
                # If there are two spaces, somewhere inside, hopefully it's between identifier and title
                split1 = list(filter(lambda x: len(x), identificator_and_title.split(two_spaces)))
                if len(split1) == 2:
                    index_part, name_part = split1[0].strip(), split1[1].strip()
            else:
                split2 = identificator_and_title.rsplit(". ", 1)
                if len(split2) == 2:
                    index_part, name_part = split2[0].strip(), split2[1].strip()

            answer2.append((index_part, name_part, page_number_int))

        return answer2


class Parser2:
    """
        anything anything number

        This is slightly more general than parser1, but that also means it has a lot more FPs.
    """
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
                answer.append((identificator.strip(), name.strip(), int(page.strip())))

            except ValueError as _:
                pass
        return answer


class DecolumnLines:
    @staticmethod
    def __two_column_format_align_check(line: str) -> Tuple[int, int, int]:
        space_sep = "    "

        dots1 = line.find(DOTS_SEP)
        space1 = line.find(space_sep, dots1 + 2)
        dots2 = line.find(DOTS_SEP, space1 + 2)
        return dots1, space1, dots2

    @staticmethod
    def __check_for_two_columns(lines: List[str]) -> bool:
        suspected_two_columns = 0

        for line in lines:
            dots1, space1, dots2 = DecolumnLines.__two_column_format_align_check(line)
            if dots1 == -1 or space1 == -1 or dots2 == -1:
                continue
            suspected_two_columns += 1

        if suspected_two_columns == 0:
            return False

        # logger.debug(f"{suspected_two_columns} | {len(a)} | {suspected_two_columns*100/len(a)}")
        return True

    @staticmethod
    def decolumn_lines(lines: List[str]) -> List[str]:
        if not DecolumnLines.__check_for_two_columns(lines):
            return lines

        # logger.debug("Possible two columns detected. Splitting the lines")
        new_lines = []

        for line in lines:
            dots1, space1, dots2 = DecolumnLines.__two_column_format_align_check(line)
            if space1 == -1:
                new_lines.append(line)
                continue
            new_lines.append(line[:space1].strip())
            new_lines.append(line[space1:].strip())
            # print(line[space1:].strip())

        return new_lines


def get_page_break_char() -> str:
    return ""


def get_page_count(lines: List[str]) -> int:
    return sum(map(lambda x: get_page_break_char() in x, lines))


class FilterLinesBySectionKeyword:
    possible_starts = ["CONTENTS:", "TABLE OF CONTENTS"]

    @staticmethod
    def filter_lines_by_section_keyword(lines: List[str]) -> int:

        section_start_line_id = FilterLinesBySectionKeyword.get_toc_section_start(lines)
        if section_start_line_id == -1:
            return []
        section_end_line_id = FilterLinesBySectionKeyword.get_first_non_empty_non_numeric_ending_line_id(lines, section_start_line_id + 1)
        if section_end_line_id == -1:
            return []

        answer = list(filter(lambda x: len(x.strip()), lines[section_start_line_id+1:section_end_line_id]))
        answer = list(filter(lambda x: x.strip()[-1].isnumeric(), answer))
        answer = list(map(lambda x: x.strip(), answer))

        # logger.debug(random_filename)
        return answer

    @staticmethod
    def get_toc_section_start(lines: List[str]) -> int:
        section_start = -1
        # max_possible_start_len = max(map(lambda x: len(x), possible_starts))
        line_id = 0

        for line in lines:
            line_stripped = line.strip().lower()
            # if len(line_stripped) > max_possible_start_len + 5:
            #     continue
            for single_start in FilterLinesBySectionKeyword.possible_starts:
                # if line_stripped.startswith(single_start.lower()):
                if line_stripped.startswith(single_start.lower()):
                    # logger.warning(line_stripped)
                    section_start = line_id
                    break
            if section_start >= 0:
                break
            line_id += 1
        return section_start

    @staticmethod
    def get_first_non_empty_non_numeric_ending_line_id(lines: List[str], start_line_id: int) -> int:
        for line_id in range(start_line_id, len(lines)):
            line_stripped = lines[line_id].strip().lower()
            if sum(map(lambda x: x.lower() in line_stripped, FilterLinesBySectionKeyword.possible_starts)):
                continue
            if line_stripped == "contents":
                continue
            if len(line_stripped) == 0:
                continue
            if not line_stripped[-1].isnumeric():
                return line_id
        return -1


class FilterLinesByNumWildcardNum:
    @staticmethod
    def filter_lines_by_num_wildcard_num(lines: List[str]) -> List[str]:
        sep = DOTS_SEP
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


if False:
    # The code here is kept so that we have it for future prototyping, but disabled so that it's not used.

    class RemoveHeadersAndFooters:
        """
            This class was a test to check whether or not we could safely remove the headers and footers of pages.
            Footers seemed to be mostly fine, but headers were a problem - in some cases there were no headers and it's not easy to detect that.
            The headers are not always static, so even checking against previous headers wouldn't help. This was abandoned.
        """

        @staticmethod
        def remove_header_and_footer(lines: List[str]) -> List[str]:
            page_breaks = []
            page_break_char = get_page_break_char()

            for i in range(len(lines)):
                if page_break_char in lines[i]:
                    page_breaks.append(i)

            footer_and_header_ofsets = []
            for i in range(len(page_breaks) - 1):
                footer_and_header_ofsets.append(
                    RemoveHeadersAndFooters.__count_non_empty_lines_before_and_after(lines, page_breaks[i]))
            footer_offset_min = min(map(lambda x: x[0], footer_and_header_ofsets))
            # header_offset_min = min(map(lambda x: x[1], footer_and_header_ofsets))
            header_offset_min = 0

            if footer_offset_min > 5:
                footer_offset_min = 0

            # logger.debug((footer_offset_min, header_offset_min))

            cur_row = 0
            answer = []
            for i in range(len(page_breaks) - 1):
                answer += lines[cur_row:max(0, page_breaks[i] - footer_offset_min)]
                cur_row = min(len(lines), page_breaks[i] + header_offset_min)

            answer += lines[cur_row:len(lines)]
            # logger.debug(page_breaks)

            return answer

        @staticmethod
        def __count_non_empty_lines_before_and_after(lines: List[str], line_index: int) -> Tuple[int, int]:
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


    class FilterChaptersDirectlyFromText:
        """
            This approach is not viable, because it also extracts for example numerical lists
        """
        @staticmethod
        def filter_chapters_directly_from_text(lines: List[str]) -> List[str]:
            answer = []
            for line in lines:
                line_stripped = line.strip()
                if len(line_stripped) == 0:
                    continue
                if not line_stripped[0].isnumeric():
                    continue
                if "." not in line_stripped:
                    continue
                answer.append(line_stripped + "\n")

            # random_filename = f"results/tmp/" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10)) + ".txt"
            # with open(random_filename, "w", encoding="utf8") as f:
            #     f.writelines(answer)

            return answer

