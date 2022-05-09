from abc import ABC, abstractmethod
from enum import IntEnum, auto
from typing import NamedTuple


class HashType(IntEnum):
    INTEGER = auto()
    BOOLEAN = auto()
    STRING = auto()


class HashKey(NamedTuple):
    hash_type: HashType
    value: int


class MObject(ABC):
    @abstractmethod
    def __repr__(self):
        pass

    def type_desc(self) -> str:
        return self.__class__.__name__


class MValue(MObject):
    __match_args__ = ("value",)

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return str(self.value)


class Hashable(MValue):
    @abstractmethod
    def hash_type(self) -> HashType:
        pass

    def hash_key(self):
        return HashKey(self.hash_type(), hash(self.value))


class MInteger(Hashable):
    def hash_type(self) -> HashType:
        return HashType.INTEGER

    def __neg__(self):
        return MInteger(-self.value)

    def __add__(self, other):
        return MInteger(self.value + other.value)

    def __sub__(self, other):
        return MInteger(self.value - other.value)

    def __mul__(self, other):
        return MInteger(self.value * other.value)

    def __truediv__(self, other):
        return MInteger(self.value / other.value)

    def __lt__(self, other):
        return self.value < other.value

    def __eq__(self, other):
        match other:
            case MInteger(value):
                return self.value == value
            case _:
                return False


class MReturnValue(MObject):
    __match_args__ = ("value",)

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return repr(self.value)


class MError(MObject):
    def __init__(self, message: str):
        self.message = message

    def __repr__(self):
        return f"ERROR: {self.message}"


class MString(Hashable):

    def hash_type(self) -> HashType:
        return HashType.STRING

    def __add__(self, other):
        return MString(self.value + other.value)


class MBoolean(Hashable):

    @staticmethod
    def from_bool(value: bool):
        return TRUE if value else FALSE

    def hash_type(self) -> HashType:
        return HashType.BOOLEAN

    def __eq__(self, other):
        match other:
            case MBoolean(value):
                if self is other:
                    return True
                else:
                    return self.value == value
            case _:
                return False


TRUE = MBoolean(True)
FALSE = MBoolean(False)


class MNull(MObject):
    def __repr__(self):
        return "null"


NULL = MNull()


class MFunction(MObject):
    def __init__(self, parameters, body, env):
        self.parameters = parameters
        self.body = body
        self.env = env

    def __repr__(self):
        if self.parameters is None:
            parameters = ""
        else:
            parameters = ", ".join(str(parameter) for parameter in self.parameters)
        return f"fn({parameters}) {{\n\t{self.body}\n}}"


class MBuiltinFunction(MObject):

    def __init__(self, fn):
        self.fn = fn

    def __repr__(self):
        return "builtin function"


class MArray(MObject):
    __match_args__ = ("elements",)

    def __init__(self, elements):
        self.elements = elements

    def __repr__(self):
        return f"[{', '.join(str(elements) for elements in self.elements)}]"


class MHash(MObject):
    __match_args__ = ("pairs",)

    def __init__(self, pairs):
        self.pairs = pairs

    def __repr__(self):
        return "{{0}}".format(str({f"{key!r}:{value!r}" for key, value in self.pairs.items()}))


def _arg_size_check(expected_size, args, body):
    length = len(args)
    if length == expected_size:
        return body(args)
    else:
        return MError(f"wrong number of arguments. got={length}, want={expected_size}")


def _array_check(name, args, body):
    array = args[0]
    match array:
        case MArray():
            return body(array, len(array.elements))
        case _:
            return MError(f"argument to `{name}` must be ARRAY, got {array.type_desc()}")


def _len(args):
    def body(arguments):
        arg = arguments[0]
        match arg:
            case MString(value):
                return MInteger(len(value))
            case MArray(elements):
                return MInteger(len(elements))
            case _:
                return MError(f"argument to `len` not supported, got {arg.type_desc()}")

    return _arg_size_check(1, args, body)


def _push(args):
    def body(array, _):
        array.elements.append(args[1])
        return MArray(array.elements)

    return _arg_size_check(2, args, lambda arguments: _array_check(PUSH_NAME, arguments, body))


def _first(args):
    def body(array, length):
        return array.elements[0] if length > 0 else NULL

    return _arg_size_check(1, args, lambda arguments: _array_check(FIRST_NAME, arguments, body))


def _last(args):
    def body(array, length):
        return array.elements[length - 1] if length > 0 else NULL

    return _arg_size_check(1, args, lambda arguments: _array_check(LAST_NAME, arguments, body))


def _rest(args):
    def body(array, length):
        if length <= 0:
            return NULL
        del array.elements[0]
        return MArray(array.elements)

    return _arg_size_check(1, args, lambda arguments: _array_check(REST_NAME, arguments, body))


LEN_NAME = "len"
PUSH_NAME = "push"
FIRST_NAME = "first"
LAST_NAME = "last"
REST_NAME = "rest"
BUILTINS = {LEN_NAME: MBuiltinFunction(_len),
            PUSH_NAME: MBuiltinFunction(_push),
            FIRST_NAME: MBuiltinFunction(_first),
            LAST_NAME: MBuiltinFunction(_last),
            REST_NAME: MBuiltinFunction(_rest)}
