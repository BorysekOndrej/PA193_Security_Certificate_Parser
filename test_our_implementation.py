import dataset.output_compare as official_tester
import utils
import math
from os.path import basename
from pprint import pprint
from loguru import logger
from typing import List, Tuple, Optional, Dict


def score_all_json_files(filename_tuples: List[Tuple[str, str, Optional[str]]]) -> dict:
    results = {}

    for single_file_tuple in filename_tuples:
        input_filename, output_filename, correct_filename = single_file_tuple
        try:
            base_filename = basename(input_filename)
            results[base_filename] = {}

            actual = utils.load_file_json(output_filename)
            expected = utils.load_file_json(correct_filename)

            checks = (official_tester.check_title, official_tester.check_versions, official_tester.check_toc, official_tester.check_revisions, official_tester.check_bibliography)
            
            results[base_filename]["sum"] = 0

            for check in checks:
                test_name = check.__name__
                results[base_filename][test_name] = 0
                try:
                    cur_result = check(actual, expected)
                    # if test_name == "check_title" and cur_result < 10:
                    #     logger.debug(f'{cur_result}\n{expected["title"]}\n{actual["title"]}\n')
                    results[base_filename][test_name] = cur_result
                    results[base_filename]["sum"] += cur_result
                except Exception as e:
                    logger.info(f'Exception on input {input_filename} and test {test_name}: {e}')
                    pass
        except Exception as e:
            logger.info(f'Exception on input {input_filename}: {e}')
            raise
            pass
    
    return results


def statistics(raw_results: dict) -> Tuple[Dict[str, float], Dict[str, float]]:
    answer_avg = {}
    answer_max = {}

    for filename in raw_results:
        for test_name in raw_results[filename]:
            answer_avg[test_name] = answer_avg.get(test_name, 0) + raw_results[filename][test_name]
            answer_max[test_name] = max(answer_max.get(test_name, 0), raw_results[filename][test_name])

    for test_name in answer_avg:
        answer_avg[test_name] = answer_avg[test_name]/len(raw_results)

    return answer_avg, answer_max


# def normalize_expected_jsons():
#     for input_filename in utils.list_input_files():
#         utils.normalize_json_file(utils.input_filename_to_expected_output_filename(input_filename))


def main(filename_tuples: List[Tuple[str, str, Optional[str]]]):
    # normalize_expected_jsons()
    raw_results = score_all_json_files(filename_tuples)
    stats_avg, stats_max = statistics(raw_results)

    print(f"Number of documents: {len(raw_results)}")

    print("Avg score:")
    pprint(stats_avg)

    print("Max score:")
    pprint(stats_max)


if __name__ == "__main__":
    main()

