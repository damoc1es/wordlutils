from abstract import *
from utils import *
from ctrl import Controller
import datetime


class NerdleGame(AbstractGame):
    def __init__(self, date: datetime.date, tries: list[str], results: list[str], solution: str):
        self.date = date
        self.tries = tries
        self.results = results
        self.solution = solution

    @staticmethod
    def from_repr(representation: str):
        date0, tries, results, solution = representation.split(",")
        date = datetime.datetime.strptime(date0, "%Y-%m-%d").date()
        return NerdleGame(date, tries.split(), results.split(), solution)
    
    def __repr__(self):
        return f"{self.date.isoformat()},{' '.join(self.tries)},{' '.join(self.results)},{self.solution}"

    def __str__(self):
        s = f"{self.date} | {self.solution}"
        for r, t in list(zip(self.results, self.tries)):
            s += f"\n{result_to_colored_box(r)} {t}"
        return s


class NerdleSimulation(AbstractSimulation):
    def __init__(self, solution: str):
        self.solution = solution
    
    def result(self, equation: str) -> str:
        eq_chars = list(equation)
        winner = list(self.solution)
        res = [ResultKey.GRAY for _ in range(8)]

        for i, c in enumerate(eq_chars):
            if c == winner[i]:
                res[i] = ResultKey.GREEN
                eq_chars[i] = winner[i] = ResultKey.GRAY
        
        for i, c in enumerate(eq_chars):
            if c != ResultKey.GRAY and c in winner:
                res[i] = ResultKey.YELLOW
                eq_chars[i] = winner[winner.index(c)] = ResultKey.GRAY

        return "".join(res)


class NerdleRunner(AbstractRunner):
    def __init__(self):
        raise NotImplementedError("NerdleRunner is not implemented yet")
    
    def add_try(self):
        raise NotImplementedError("NerdleRunner is not implemented yet")
    
    def get_data(self):
        raise NotImplementedError("NerdleRunner is not implemented yet")

    @staticmethod
    def validate_try(string: str, result: str|None = None) -> None:
        if len(string) != 8:
            raise ValueError("Invalid length. Must be 8 characters long.")
        if not set(string).issubset(set("1234567890+-*/=")):
            raise ValueError("Invalid characters. Must be digits or operators.")
        if result is not None:
            if len(result) != 8:
                raise ValueError("Invalid length. Must be 8 characters long.")
            if not set(result).issubset(set([ResultKey.GRAY, ResultKey.YELLOW, ResultKey.GREEN])):
                raise ValueError("Invalid characters. Must be one of 'G', 'Y', '_'.")


class NerdleCtrl(Controller):
    def __init__(self, repo):
        self.repo = repo
        super().__init__(NerdleRunner)

    def get_possible_solutions(self):
        if self.runner is None:
            raise Exception("Game not started.")
        raise NotImplementedError("NerdleRunner is not implemented yet")
