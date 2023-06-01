from enum import Enum


class ResultKey:
    GRAY = '_'
    YELLOW = 'Y'
    GREEN = 'G'

def result_to_colored_box(string):
    res = ""
    for c in string:
        match c:
            case ResultKey.GRAY:
                res += '⬛'
            case ResultKey.YELLOW:
                res += '🟨'
            case ResultKey.GREEN:
                res += '🟩'
            case _:
                res += c
    return res

class GameType(Enum):
    NONE = 0
    WORDLE = 1
    NERDLE = 2

WORDS_LIST_LINK = 'https://raw.githubusercontent.com/tabatkins/wordle-list/main/words'
