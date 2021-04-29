import os
import afl
import sys

from ParseDocument import ParseDocument, ParsingResult

pd = ParseDocument([], correct_solution=None)
sys.stdin.reconfigure(encoding='utf8')

afl.init()
pd = ParseDocument(sys.stdin.readlines(), correct_solution=None)
parsing_result: ParsingResult = pd.get_results()
os._exit(0)
