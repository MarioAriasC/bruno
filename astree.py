import abc
from abc import ABC

from tokens import Token


class Node(ABC):
    @abc.abstractmethod
    def token_literal(self) -> str:
        pass

    @abc.abstractmethod
    def __str__(self) -> str:
        pass

    def __eq__(self, other):
        return str(other) == str(self) if other is not None else False

    @abc.abstractmethod
    def __hash__(self):
        pass


class Statement(Node):
    @abc.abstractmethod
    def token(self) -> Token:
        pass

    def token_literal(self) -> str:
        return self.token().literal


class Expression(Node):
    @abc.abstractmethod
    def token(self) -> Token:
        pass

    def token_literal(self) -> str:
        return self.token().literal


class Identifier(Expression):
    __match_args__ = ("value",)

    def __init__(self, token: Token, value: str):
        self._token = token
        self.value = value

    def __str__(self) -> str:
        return self.value

    def token(self) -> Token:
        return self._token

    def __hash__(self):
        return hash(str(self))


class LetStatement(Statement):
    __match_args__ = ("name", "value")

    def __init__(self, token: Token, name: Identifier, value: Expression | None):
        self._token = token
        self.name = name
        self.value = value

    def token(self) -> Token:
        return self._token

    def __str__(self) -> str:
        return f"{self.token_literal()} {self.name} = {self.value}"

    def __hash__(self):
        return hash(str(self))


class ExpressionStatement(Statement):
    __match_args__ = ("expression",)

    def __init__(self, token: Token, expression: Expression | None):
        self._token = token
        self.expression = expression

    def token(self) -> Token:
        return self._token

    def __str__(self) -> str:
        return str(self.expression)

    def __hash__(self):
        return hash(str(self))


class Program(Node):
    __match_args__ = ("statements",)

    def __init__(self, statements: list[Statement]):
        self.statements = statements

    def token_literal(self) -> str:
        return "" if len(self.statements) == 0 else self.statements[0].token_literal()

    def __str__(self) -> str:
        return "".join((str(statement) for statement in self.statements))

    def __hash__(self):
        return hash(str(self))


class LiteralExpression(Expression):
    __match_args__ = ("value",)

    def __init__(self, token: Token, value):
        self._token = token
        self.value = value

    def token(self) -> Token:
        return self._token

    def __str__(self) -> str:
        return self.token().literal

    def __hash__(self):
        return hash(str(self))


class IntegerLiteral(LiteralExpression):
    pass


class BooleanLiteral(LiteralExpression):
    pass


class ReturnStatement(Statement):
    __match_args__ = ("return_value",)

    def __init__(self, token: Token, return_value: Expression | None):
        self._token = token
        self.return_value = return_value

    def token(self) -> Token:
        return self._token

    def __str__(self) -> str:
        return f"{self.token_literal()} {self.return_value}"

    def __hash__(self):
        return hash(str(self))


class PrefixExpression(Expression):
    __match_args__ = ("operator", "right")

    def __init__(self, token: Token, operator: str, right: Expression | None):
        self._token = token
        self.operator = operator
        self.right = right

    def token(self) -> Token:
        return self._token

    def __str__(self) -> str:
        return f"({self.operator}{self.right})"

    def __hash__(self):
        return hash(str(self))


class InfixExpression(Expression):
    __match_args__ = ("left", "operator", "right")

    def __init__(
            self,
            token: Token,
            left: Expression | None,
            operator: str,
            right: Expression | None,
    ):
        self._token = token
        self.left = left
        self.operator = operator
        self.right = right

    def token(self) -> Token:
        return self._token

    def __str__(self) -> str:
        return f"({self.left} {self.operator} {self.right})"

    def __hash__(self):
        return hash(str(self))


class CallExpression(Expression):
    __match_args__ = ("function", "arguments")

    def __init__(
            self,
            token: Token,
            function: Expression | None,
            arguments: list[Expression | None] | None,
    ):
        self._token = token
        self.function = function
        self.arguments = arguments

    def token(self) -> Token:
        return self._token

    def __str__(self) -> str:
        return f'{self.function}({", ".join(str(argument) for argument in self.arguments)})'

    def __hash__(self):
        return hash(str(self))


class ArrayLiteral(Expression):
    __match_args__ = ("elements",)

    def __init__(self, token: Token, elements: list[Expression | None] | None):
        self._token = token
        self.elements = elements

    def token(self) -> Token:
        return self._token

    def __str__(self) -> str:
        return f'[{", ".join(str(element) for element in self.elements)}]'

    def __hash__(self):
        return hash(str(self))


class IndexExpression(Expression):
    __match_args__ = ("left", "index")

    def __init__(self, token: Token, left: Expression | None, index: Expression | None):
        self._token = token
        self.left = left
        self.index = index

    def token(self) -> Token:
        return self._token

    def __str__(self) -> str:
        return f"({self.left}[{self.index}])"

    def __hash__(self):
        return hash(str(self))


class BlockStatement(Statement):
    def __init__(self, token: Token, statements: list[Statement | None] | None):
        self._token = token
        self.statements = statements

    def token(self) -> Token:
        return self._token

    def __str__(self) -> str:
        return (
            ""
            if self.statements is None
            else "".join(str(statement) for statement in self.statements)
        )

    def __hash__(self):
        return hash(str(self))


class IfExpression(Expression):
    def __init__(
            self,
            token: Token,
            condition: Expression | None,
            consequence: BlockStatement | None,
            alternative: BlockStatement | None,
    ):
        self._token = token
        self.condition = condition
        self.consequence = consequence
        self.alternative = alternative

    def token(self) -> Token:
        return self._token

    def __str__(self) -> str:
        alt = f"else {self.alternative}" if self.alternative is not None else ""
        return f"{self.condition} {self.consequence} {alt}"

    def __hash__(self):
        return hash(str(self))


class FunctionLiteral(Expression):
    __match_args__ = ("parameters", "body")

    def __init__(
            self,
            token: Token,
            parameters: list[Identifier] | None,
            body: BlockStatement | None,
    ):
        self._token = token
        self.parameters = parameters
        self.body = body

    def token(self) -> Token:
        return self._token

    def __str__(self) -> str:
        return f"{self.token_literal()}({', '.join(str(parameter) for parameter in self.parameters)}) {self.body}"

    def __hash__(self):
        return hash(str(self))


class StringLiteral(Expression):
    __match_args__ = ("value",)

    def __init__(self, token: Token, value: str):
        self._token = token
        self.value = value

    def token(self) -> Token:
        return self._token

    def __str__(self) -> str:
        return self.value

    def __hash__(self):
        return hash(str(self))


class HashLiteral(Expression):
    __match_args__ = ("pairs",)

    def __init__(self, token: Token, pairs: dict[Expression, Expression]):
        self._token = token
        self.pairs = pairs

    def token(self) -> Token:
        return self._token

    def __str__(self) -> str:
        return "{{0}}".format(
            ", ".join(f"{key}:{self.pairs[key]}" for key in self.pairs.keys())
        )

    def __hash__(self):
        return hash(str(self))
