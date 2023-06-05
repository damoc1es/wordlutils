from abstract import *
from utils import *
from ctrl import Controller
import datetime
import requests


class WordleGame(AbstractGame):
    NAME = "WORDLE"

    def __init__(self, date: datetime.date, tries: list[str], results: list[str], solution: str):
        self.date = date
        self.tries = [t.upper() for t in tries]
        self.results = results
        self.solution = solution.upper()

    @staticmethod
    def from_repr(representation: str):
        date0, tries, results, solution = representation.split(",")
        date = datetime.datetime.strptime(date0, "%Y-%m-%d").date()
        return WordleGame(date, tries.split(), results.split(), solution)

    def __repr__(self):
        return f"{self.date.isoformat()},{' '.join(self.tries)},{' '.join(self.results)},{self.solution}"

    def __str__(self):
        s = f"{self.date} | {self.solution}"
        for r, t in list(zip(self.results, self.tries)):
            s += f"\n{result_to_colored_box(r)} {t}"
        return s


class WordleSimulation(AbstractSimulation):
    def __init__(self, solution: str):
        self.solution = solution.lower()
    
    def result(self, word: str) -> str:
        word_chars = list(word.lower())
        winner = list(self.solution)
        res = [ResultKey.GRAY for _ in range(5)]

        for i, c in enumerate(word_chars):
            if c == winner[i]:
                res[i] = ResultKey.GREEN
                word_chars[i] = winner[i] = ResultKey.GRAY
        
        for i, c in enumerate(word_chars):
            if c != ResultKey.GRAY and c in winner:
                res[i] = ResultKey.YELLOW
                word_chars[i] = winner[winner.index(c)] = ResultKey.GRAY

        return "".join(res)


class WordleRunner(AbstractRunner):
    def __init__(self):
        self.green_chars: dict[int, str|None] = {1: None, 2: None, 3: None, 4: None, 5: None}
        self.yellow_chars = {1: "", 2: "", 3: "", 4: "", 5: ""}
        self.gray_chars = ""
        self.solution = None

        self.tries = []
        self.results = []

    def add_try(self, word_tried: str, result: str) -> None:
        WordleRunner.validate_try(word_tried, result)
        
        word_tried = word_tried.lower()
        self.tries.append(word_tried)

        if set(result) == ResultKey.GREEN:
            self.solution = word_tried
            return

        i = 0
        for c, t in zip(word_tried, result):
            i += 1
            
            match t:
                case ResultKey.GRAY:
                    if word_tried.count(c) == 1:
                        self.gray_chars += c
                    else:
                        for c2, t2 in zip(word_tried, result):
                            if c2 == c and t2 == ResultKey.GREEN:
                                self.yellow_chars[i] += c
                                break
                case ResultKey.YELLOW:
                    self.yellow_chars[i] += c
                case ResultKey.GREEN:
                    self.green_chars[i] = c
                case _:
                    raise Exception("Invalid result character found.")
    
    def get_data(self):
        return self.gray_chars, self.yellow_chars, self.green_chars 

    @staticmethod
    def validate_try(string: str, result: str|None = None) -> None:
        if len(string) != 5:
            raise ValueError("Invalid length. Must be 5 characters long.")
        if not string.isalpha():
            raise ValueError("Invalid characters. Must be alphabetic.")
        if result is not None:
            if len(result) != 5:
                raise ValueError("Invalid length. Must be 5 characters long.")
            if not set(result).issubset(set([ResultKey.GRAY, ResultKey.YELLOW, ResultKey.GREEN])):
                raise ValueError("Invalid characters. Must be one of 'G', 'Y', '_'.")


class WordleCtrl(Controller):
    def __init__(self, repo, all_words_source=WORDS_LIST_LINK):
        self.repo = repo
        super().__init__(WordleRunner)
        r = requests.get(all_words_source)
        self.all_words = r.text.split('\n')

    def get_possible_solutions(self):
        if self.runner is None:
            raise Exception("Game not started.")
        
        grays, yellows, greens = self.runner.get_data()

        filtered = list(filter(lambda x: len(set(x) & set(grays)) == 0, self.all_words)) # gray
        filtered = list(filter(lambda x: all([x[i] not in yellows[i+1] for i in range(5)]), filtered)) # yellow

        for y in yellows.values(): # yellow
            if y != "":
                filtered = list(filter(lambda x: all([c in x for c in y]), filtered))
        
        filtered = list(filter(lambda x: all([True if greens[i+1] is None else x[i] == greens[i+1] for i in range(5)]), filtered)) # green

        return filtered
