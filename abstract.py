from abc import ABC, abstractmethod


class AbstractGame(ABC):
    @staticmethod
    @abstractmethod
    def from_repr(representation: str):
        ...


class AbstractSimulation(ABC):
    @abstractmethod
    def result(self, string: str) -> list[str]:
        ...


class AbstractRunner(ABC):
    @abstractmethod
    def add_try(self, string: str, result: str) -> None:
        ...

    @abstractmethod
    def get_data(self):
        ...
    
    @staticmethod
    @abstractmethod
    def validate_try(string: str):
        ...
