from utils import *
from abc import ABC, abstractmethod
import datetime


class Controller(ABC):
    def __init__(self, runner_class):
        self.runner_class = runner_class
        self.runner = None

    @property
    def runner(self):
        return self._runner
    
    @property
    def repo(self):
        return self._repo

    @runner.setter
    def runner(self, value):
        self._runner = value
    
    @repo.setter
    def repo(self, value):
        self._repo = value

    def start(self):
        self.runner = self.runner_class()
    
    def add_try(self, tried: str, result: str) -> None:
        if self.runner is None:
            raise Exception("Game not started.")
        self.runner.add_try(tried, result)
    
    def store(self, game):
        self.repo.add(game)
    
    def get(self, date = None):
        return self.repo.get(date)
    
    def backup(self):
        return self.repo.backup(datetime.datetime.now())

    def get_stats(self):
        dates = []
        scores = []
        games = self.repo.get_all()

        for game in games:
            dates.append(game.date)
            score = len(game.results)
            if set(game.results[-1]) != set([ResultKey.GREEN]):
                score += 1
            scores.append(score)
        
        return dates, scores

    @abstractmethod
    def get_possible_solutions(self):
        ...
