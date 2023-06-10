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
    
    def get_longest_streak(self):
        games = self.repo.get_all()
        if len(games) == 0:
            return None
        
        max_streak = 0
        date1 = date2 = games[0].date

        current_streak = 1
        for i in range(len(games)-1):
            game1 = games[i]
            game2 = games[i+1]

            if (game2.date - game1.date).days == 1:
                current_streak += 1
                date2 = game2.date
            else:
                date1 = game1.date
                current_streak = 1
            
            if current_streak > max_streak:
                max_streak = current_streak
                
        
        return max_streak, date1, date2

    def get_current_streak(self):
        games = self.repo.get_all()
        if len(games) == 0:
            return None
        
        if games[-1].date not in (datetime.date.today() - datetime.timedelta(days=1), datetime.date.today()):
            return None

        current_streak = 1
        for i in range(len(games)-1, 0, -1):
            game1 = games[i]
            game2 = games[i-1]

            if (game1.date - game2.date).days == 1:
                current_streak += 1
            else: break
        
        return current_streak

    @abstractmethod
    def get_possible_solutions(self):
        ...
