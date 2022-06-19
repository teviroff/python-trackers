"""Module with non-threaded trackers. Defines `ForTracker` and `WhileTracker`"""

from typing import TypeVar, Iterable, Generic
from abc import ABCMeta, abstractmethod
from time import perf_counter


_T = TypeVar('_T')


class Tracker(metaclass=ABCMeta):

    name: str
    start_time: float

    def __init__(self, name: str):
        self.name = name
        self.start_time = perf_counter()
    
    @abstractmethod
    def _get_msg(self) -> str:
        ...
    
    @abstractmethod
    def _get_end(self) -> str:
        ...

    def print(self) -> None:
        print(self._get_msg(), end=self._get_end())


class LoopTracker(Tracker):
    def __init__(self, name: str):
        super().__init__(name)
        self.it_i = -1
        self._stop = False
    
    def _get_end(self) -> str:
        return '\n' if self._stop else '\r'


class ForTracker(LoopTracker, Generic[_T]):
    """
    ## General \n
    For loop tracker. Tracks the progress of execution of for loop by providing current
    iteration index and, if possible, the length of the iterable that has been provided.\n
    ## Use-case \n
    Imagine you have some loop with iterable object:\n
    >>> for i in iterable: ... \n
    In order to track progress of this loop execution, you should wrap `iterable` with `ForTracker` \n
    >>> for i in ForTracker('name', iterable): ... \n
    The output produced by this action will look like this: \n
    `(1/10) name - 1.08s` or `(1) name - 1.08s` depending on ability to get iterable length. \n
    Also if you want to use enumerate, you can provide optional `enum` argument. \n
    >>> for i, val in ForTracker('name', iterable, True): ...\n
    ## Other \n
    Other details about the functionality and source code may be found on [GitHub](https://github.com/teviroff/python-trackers)
    """

    def __init__(self, name: str, it: Iterable[_T], enum=False):
        super().__init__(name)
        self.it = it
        self.enum = enum
        self.has_length = False
        try:
            self.it_len = len(it)
            self.has_length = True
        except TypeError:
            pass

    def __iter__(self):
        self._it = self.it.__iter__()
        self.print()
        return self
    
    def __next__(self) -> _T:
        try:
            r_i, r_val = self.it_i, self._it.__next__()
            self.it_i += 1
        except StopIteration:
            self._stop = True
            self.print()
            raise StopIteration
        self.print()
        if self.enum:
            return r_i, r_val
        return r_val
    
    def _get_msg(self) -> str:
        if self.has_length:
            return f'({self.it_i + 1}/{self.it_len}) {self.name} - ' \
                f'{perf_counter() - self.start_time:.2f}s'
        return f'({self.it_i}) {self.name} - {perf_counter() - self.start_time:.2f}s'


class WhileTrackerMeta(ABCMeta):
    _instances = {}
    def __call__(cls, name: str, expr: bool, *args, **kwargs):
        if hash((cls, name)) not in cls._instances:
            cls._instances[hash((cls, name))] = super().__call__(name, expr, *args, **kwargs)
        cls._instances[hash((cls, name))].expr = expr
        return cls._instances[hash((cls, name))]


class WhileTracker(LoopTracker, metaclass=WhileTrackerMeta):
    """
    ## General \n
    While loop tracker. Tracks the progress of execution of while loop by showing indicator
    that updates each cycle iteration. \n
    ## Use-case \n
    Imagine you have while loop with some condition: \n
    >>> while condition: ... \n
    In order to track this loop execution, you should wrap `condition` with `WhileTracker` \n
    >>> while WhileTracker('name', condition): ... \n
    The output produced by this action will look like this: \n
    `> (-) name - 1.08s` and each iteration progress will change to next symbol in `_prog`, 
    by default `_prog = ['-', '\\\', '|', '/']` \n
    ## Other \n
    Other details about the functionality and source code may be found on [GitHub](https://github.com/teviroff/python-trackers)
    """
    
    _prog = ['-', '\\', '|', '/']

    def __init__(self, name: str, expr: bool):
        super().__init__(name)
        self.expr = expr
    
    def __bool__(self):
        self._stop = not self.expr
        self.it_i += 1
        self.print()
        return self.expr
    
    def _get_msg(self) -> str:
        return f'({self._prog[self.it_i % len(self._prog)]}) {self.name} - ' \
               f'{perf_counter() - self.start_time:.2f}s'
