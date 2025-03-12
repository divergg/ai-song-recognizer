from abc import (
    ABC,
    abstractmethod,
)


class IDatabaseRepository(ABC):

    @abstractmethod
    def find_one(self, **kwargs): ...

    @abstractmethod
    def insert_one(self, **kwargs): ...
