"""Module with miscellaneaous functions and classes, needed for trackers package."""

from threading import Thread, Event
from typing import Sized


class InfSeq:
    """Class for constructing infinite sequence from sized iterable."""
    
    seq: Sized
    i: int

    def __init__(self, seq: Sized):
        self.seq = seq
        self.i = 0

    def __iter__(self):
        return self
    
    def __next__(self):
        if self.i == len(self.seq):
            self.i = 0
        r = self.seq[self.i]
        self.i += 1
        return r
    
    def __len__(self):
        return float('inf')


class StoppableThread(Thread):
    """Thread subclass, that implements functionality to stop thread 
    (adds event, that should be tracked in order to stop thread execution).
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stop_event = Event()
    
    def stop(self) -> None:
        """Function to set stop event. After calling, property `is_stopped` will be `True`"""

        self.stop_event.set()
    
    @property
    def is_stopped(self) -> bool:
        return self.stop_event.is_set()


def cls_decorator_w_kwargs(cls, func, **kwargs):
    if func is not None:
        return cls(func)
    else:
        def wrapper(func):
            return cls(func, **kwargs)
        return wrapper
