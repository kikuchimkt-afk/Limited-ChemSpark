import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'questions')
from _restructure_chapter import _convert_standalone_numbers, STANDALONE_NUM_RE
import re

test = "約四・〇"
print(f"Input: {test}")
matches = list(STANDALONE_NUM_RE.finditer(test))
print(f"Matches: {[(m.group(), m.start(), m.end()) for m in matches]}")
result = _convert_standalone_numbers(test)
print(f"Result: {result}")

test2 = "約三・四"
print(f"\nInput: {test2}")
matches2 = list(STANDALONE_NUM_RE.finditer(test2))
print(f"Matches: {[(m.group(), m.start(), m.end()) for m in matches2]}")
result2 = _convert_standalone_numbers(test2)
print(f"Result: {result2}")

# 〇 is not in the decimal digit class [零一二三四五六七八九]
print(f"\n'〇' in 零一二三四五六七八九: {'〇' in '零一二三四五六七八九'}")
print(f"'零' in 零一二三四五六七八九: {'零' in '零一二三四五六七八九'}")
print(f"ord('〇')={ord('〇')}, ord('零')={ord('零')}")
