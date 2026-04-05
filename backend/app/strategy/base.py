from abc import ABC, abstractmethod
from app.core.types import Bar, Signal

class Strategy(ABC):
    name: str

    @abstractmethod
    def on_bar(self, bar: Bar, portfolio, state) -> list[Signal]:
        pass