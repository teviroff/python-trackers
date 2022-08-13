"""Module with non-threaded trackers."""

from typing import Any, Callable, TypeVar, Iterable, Generic
from abc import ABCMeta, abstractmethod
from time import perf_counter
from trackers import misc


_T = TypeVar('_T')


class Tracker(metaclass=ABCMeta):
    """Abstract base class for all trackers."""

    name: str
    call_time: float

    def __init__(self, name: str):
        self.name = name
        self.call_time = perf_counter()
    
    @abstractmethod
    def get_msg(self) -> str:
        """Method for obtaining message, printed to console."""
        ...
    
    @abstractmethod
    def get_end(self) -> str:
        """Method for obtaining end of message to print (`\\n` or `\\r` usually)."""
        ...

    def print(self) -> None:
        """Method, used for printing to console. Combines `get_msg` and `get_end` methods."""

        print(self.get_msg(), end=self.get_end())
    
    @property
    def dtime(self) -> float:
        """Property with time delta between tracker `call_time` and current time."""

        return perf_counter() - self.call_time


class LoopTracker(Tracker):
    """Abstract base class for all non-threaded loop trackers."""

    it_i: int
    end: bool

    def __init__(self, name: str):
        super().__init__(name)
        self.it_i = 0
        self.end = False
    
    def get_end(self) -> str:
        return '\n' if self.end else '\r'


class ForTracker(LoopTracker, Generic[_T]):
    """
    ## General
    For loop tracker. Tracks the progress of execution of for loop by 
    providing current iteration index and, if possible, the length of the iterable 
    that has been provided and the elapsed time since start of loop execution.\n
    ## Use-case
    Imagine you have some loop with `Iterable` object: \n
    ```
    for i in iterable: ...
    ```
    In order to track progress of this loop execution, you should wrap `Iterable` with `ForTracker` \n
    ```
    for i in ForTracker('loop', iterable): ...
    # (1/10) loop - 1.08s or
    # (1) loop - 1.08s if iterable is not sized
    ```
    There is also an optional `enumQ` argument, that implements built-in `enumerate` functionality. 
    ```
    for i, val in ForTracker('loop', enumerate(iterable)): ... # Error
    for i, val in ForTracker('loop', iterable, True): ... # Good
    ```
    ## Other \n
    Other details about the functionality and source code may be found on [GitHub](https://github.com/teviroff/python-trackers)
    """

    it: Iterable[_T]
    it_lenQ: bool
    it_len: int
    enumQ: bool
    
    def _get_len(self):
        """Private method for obtaining `Iterable` length (if possible)."""

        try:
            self.it_len = len(self.it)
            self.it_lenQ = True
        except TypeError:
            self.it_lenQ = False

    def __init__(self, name: str, it: Iterable[_T], enumQ: bool = False):
        super().__init__(name)
        self.it = it
        self._get_len()
        self.enumQ = enumQ

    def __iter__(self):
        self.it = iter(self.it)
        self.call_time = perf_counter()
        self.print()
        return self
    
    def __next__(self) -> _T:
        try:
            r_i, r_val = self.it_i, next(self.it)
        except StopIteration as e:
            self.end = True
            self.print()
            raise e
        self.print()
        self.it_i += 1
        if self.enumQ:
            return r_i, r_val
        return r_val
    
    def get_msg(self) -> str:
        if self.it_lenQ:
            return f'({self.it_i}/{self.it_len}) {self.name} - {self.dtime:.2f}s'
        return f'({self.it_i}) {self.name} - {self.dtime:.2f}s'


class WhileTrackerMeta(ABCMeta):
    """Metaclass for `WhileTracker`. Defines singleton with slight adjustments."""

    instances: dict[str, Any] = {}

    def __call__(cls, name: str, expr: bool, *args, **kwargs):
        h = hash((cls, name))
        if h not in cls.instances:
            cls.instances[h] = super().__call__(name, expr, *args, **kwargs)
        cls.instances[h].expr = expr
        return cls.instances[h]


class WhileTracker(LoopTracker, metaclass=WhileTrackerMeta):
    """
    ## General
    While loop tracker. Tracks the progress of execution of while loop by showing indicator
    that updates each cycle iteration.
    ## Use-case
    Imagine you have some while loop:
    ```
    while condition: ...
    ```
    In order to track this loop execution, you should wrap condition with `WhileTracker`:
    ```
    while WhileTracker('loop', condition): ...
    # (20) \\ loop - 1.08s, where \\ is progress indicator,
    # that will cycle trough ['-', '/', '|', '\\']
    ```
    ## Other \n
    Other details about the functionality and source code may be found on [GitHub](https://github.com/teviroff/python-trackers)
    """
    
    prog = misc.InfSeq(['-', '\\', '|', '/'])

    def __init__(self, name: str, expr: bool):
        super().__init__(name)
        self.expr = expr
    
    def __bool__(self):
        self.end = not self.expr
        self.it_i += 1
        self.print()
        return self.expr
    
    def get_msg(self) -> str:
        return f'({self.it_i}) {next(self.prog)} {self.name} - {self.dtime:.2f}s'


class _FuncTracker(Tracker):
    """
    ## General
    Function flag tracker. Tracks the progress of execution of function with flags. \n
    ## Use-case
    Imagine you have some function `foo(a, b)`: \n
    ```
    def foo(a, b): ...
    ```
    In order to track this function execution you should decorate it with `FuncTracker` and 
    add primary-positioned tracker argument: \n
    ```
    @FuncTracker(name='bar', call_msg='Some call message', exit_msg='Done!')
    def foo(tracker, a, b):
        ...
    # bar | Some call message
    # bar | Done! - 1.08s
    ```
    Notice that `call_msg` do not have time stamp, while `exit_msg` do. \n
    Also, all of the `FuncTracker` arguments are optional, so if you don't want to print call 
    or exit message, or want to use function name from code, you can do this with zero-arguments 
    form of `FuncTracker` decorator. \n
    If you want to include other flags this is done with `tracker.flag` method.
    ```
    @FuncTracker
    def foo(tracker, a, b):
        tracker.flag('some additional flag') 
        ... 
    # foo | some additional flag - 0.67s
    ```
    If you want to remove time stamp from flag message, you should provide optional `timeQ` 
    argument. (by default `timeQ = True`) \n
    Also, if you want to track variable values at some flag, you can do this by providing 
    kwargs to the `tracker.flag` method:
    ```
    @FuncTracker
    def foo(tracker, a, b):
        tracker.flag('some flag', first_arg=a, second_arg=b)
        ...
    # foo | some flag - 0.89s | first_arg=1, second_arg=2
    ```
    ## Other \n
    Other details about functionality and source code may be found on [GitHub](https://github.com/teviroff/python-trackers)
    """

    func: Callable
    call_msg: str
    exit_msg: str

    def __init__(self, func, name: str = None, call_msg: str = None, exit_msg: str = None):
        self.func = func
        self.name = func.__name__ if not name else name
        self.call_msg = call_msg
        self.exit_msg = exit_msg
    
    def flag(self, msg: str, timeQ: bool = True, **t_vars):
        """Method for placing additional flags to the function. (see @ `FuncTracker` documentation)"""

        self.print(msg, timeQ, **t_vars)

    def __call__(self, *args, **kwargs):
        self.call_time = perf_counter()
        if self.call_msg:
            self.flag(self.call_msg, False)
        r = self.func(self, *args, **kwargs)
        if self.exit_msg:
            self.flag(self.exit_msg)
        return r

    def get_msg(self, msg: str, timeQ: bool, **t_vars):
        m = f'{self.name} | {msg}'
        if timeQ:
            m += f' - {self.dtime:.2f}s'
        if t_vars:
            _ = ', '.join(f'{var}={repr(val)}' for var, val in t_vars.items())
            m += f' | {_}'
        return m
    
    def get_end(self):
        return '\n'
    
    def print(self, msg: str, timeQ: bool, **t_vars) -> None:
        print(self.get_msg(msg, timeQ, **t_vars), end=self.get_end())


def FuncTracker(func=None, *, name: str = None, call_msg: str = None, exit_msg: str = None):
    """Decorator for `_FuncTracker` class."""

    return misc.cls_decorator_w_kwargs(
        _FuncTracker, func,
        name=name, call_msg=call_msg, exit_msg=exit_msg,
    )
