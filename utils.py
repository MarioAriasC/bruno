from typing import TypeVar

T = TypeVar('T')


def nn(t: T | None) -> T:
    return t
    # if t is not None:
    #     return t
    # raise RuntimeError("Value shouldn't be null")
