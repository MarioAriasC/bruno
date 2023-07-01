from typing import TypeVar

T = TypeVar('T')


def nn(t: T | None) -> T:
    if t is not None:
        return t
    else:
        raise RuntimeError("Value shouldn't be null")
