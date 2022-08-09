"""Module with non-threaded trackers. Defines `ForTracker` and `WhileTracker`"""

from typing import Any, TypeVar, Iterable, Generic
from abc import ABCMeta, abstractmethod
from time import perf_counter
from trackers import misc


_T = TypeVar('_T')


class Tracker(metaclass=ABCMeta):
    """Abstract base class for all trackers."""

    _name: str
    _stime: float

    def __init__(self, name: str):
        self._name = name
        self._stime = perf_counter()
    
    @abstractmethod
    def _get_msg(self) -> str:
        """Method for obtaining message, printed to console."""
        ...
    
    @abstractmethod
    def _get_end(self) -> str:
        """Method for obtaining end of message to print (`\\n` or `\\r` usually)."""
        ...

    def _print(self) -> None:
        """Method, used for printing to console. Combines `_get_msg` and `_get_end` methods."""

        print(self._get_msg(), end=self._get_end())


class LoopTracker(Tracker):
    """Abstract base class for all non-threaded loop trackers."""

    _it_i: int
    _end: bool

    def __init__(self, name: str):
        super().__init__(name)
        self._it_i = 0
        self._end = False
    
    def _get_end(self) -> str:
        return '\n' if self._end else '\r'


class ForTracker(LoopTracker, Generic[_T]):
    """
    ## General \n
    Non-threaded `ForTracker` class. Tracks the progress of execution of for loop by 
    providing current iteration index and, if possible, the length of the iterable 
    that has been provided and the elapsed time since start of loop execution.\n
    ## Use-case \n
    Imagine you have some loop with `Iterable` object:\n
    >>> for i in iterable: ... \n
    In order to track progress of this loop execution, you should wrap `Iterable` with `ForTracker` \n
    >>> for i in ForTracker('name', iterable): ... \n
    The output produced by this action will look like this: \n
    `(1/10) name - 1.08s` or `(1) name - 1.08s` depending on ability to get iterable length. \n
    Also if you want to use enumerate, you can provide optional `enum` argument. \n
    >>> for i, val in ForTracker('name', iterable, True): ...\n
    ## Other \n
    Other details about the functionality and source code may be found on [GitHub](https://github.com/teviroff/python-trackers)
    """

    _it: Iterable[_T]
    _it_has_len: bool
    _it_len: int
    _enum: bool

    def __init__(self, name: str, it: Iterable[_T], enum=False):
        super().__init__(name)
        self._it = it
        self.__get_len()
        self._enum = enum
    
    def __get_len(self):
        """Private method for obtaining `Iterable` length (if possible)."""

        try:
            self._it_len = len(self._it)
            self._it_has_len = True
        except TypeError:
            self._it_has_len = False

    def __iter__(self):
        self._it = iter(self._it)
        self._print()
        return self
    
    def __next__(self) -> _T:
        try:
            r_i, r_val = self._it_i, next(self._it)
        except StopIteration as e:
            self._end = True
            self._print()
            raise e
        self._print()
        self._it_i += 1
        if self._enum:
            return r_i, r_val
        return r_val
    
    def _get_msg(self) -> str:
        if self._it_has_len:
            return f'({self._it_i}/{self._it_len}) {self._name} - ' \
                f'{perf_counter() - self._stime:.2f}s'
        return f'({self._it_i}) {self._name} - {perf_counter() - self._stime:.2f}s'


class WhileTrackerMeta(ABCMeta):
    """Metaclass for `WhileTracker`. Defines singleton with slight adjustments."""

    _instances: dict[str, Any] = {}

    def __call__(cls, name: str, expr: bool, *args, **kwargs):
        _h = hash((cls, name))
        if _h not in cls._instances:
            cls._instances[_h] = super().__call__(name, expr, *args, **kwargs)
        cls._instances[_h]._expr = expr
        return cls._instances[_h]


class WhileTracker(LoopTracker, metaclass=WhileTrackerMeta):
    """
    ## General \n
    While loop tracker. Tracks the progress of execution of while loop by showing indicator
    that updates each cycle iteration. \n
    ## Use-case \n
    Imagine you have while loop: \n
    >>> while condition: ... \n
    In order to track this loop execution, you should wrap `Condition` with `WhileTracker` \n
    >>> while WhileTracker('name', condition): ... \n
    The output, produced by this action will look like this: `(69420) \\ loop - 0.02s`, \n
    where `\\` is the progress indicator, that will cycle through `['-', '/', '|', '\\']` \n
    ## Other \n
    Other details about the functionality and source code may be found on [GitHub](https://github.com/teviroff/python-trackers)
    """
    
    _prog = misc.InfSeq(['-', '\\', '|', '/'])

    def __init__(self, name: str, expr: bool):
        super().__init__(name)
        self._expr = expr
    
    def __bool__(self):
        self._end = not self._expr
        if not self._end: self._it_i += 1
        self._print()
        return self._expr
    
    def _get_msg(self) -> str:
        return f'({self._it_i}) {next(self._prog)} {self._name} - {perf_counter() - self._stime:.2f}s'
