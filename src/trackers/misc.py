"""Module with miscellaneaous functions and classes, needed for trackers package."""

from threading import Thread, Event
from typing import Sized


class InfSeq:
    """Class for constructing infinite sequence from sized iterable."""
    
    _seq: Sized
    _i: int

    def __init__(self, seq: Sized):
        self._seq = seq
        self._i = 0

    def __iter__(self):
        return self
    
    def __next__(self):
        if self._i == len(self._seq):
            self._i = 0
        r = self._seq[self._i]
        self._i += 1
        return r
    
    def __len__(self):
        return float('inf')


class StoppableThread(Thread):
    """Thread subclass, that implements functionality to stop thread 
    (adds event, that should be tracked in order to stop thread execution).
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__stop_event = Event()
    
    def stop(self) -> None:
        """Function to set stop event. After calling, property `is_stopped` will be `True`"""

        self.__stop_event.set()
    
    @property
    def is_stopped(self) -> bool:
        return self.__stop_event.is_set()


def cls_decorator_w_kwargs(cls, func, **kwargs):
    if func is not None: # if called decorator with no args
        return cls(func)
    else:
        def wrapper(func):
            return cls(func, **kwargs)
        return wrapper
