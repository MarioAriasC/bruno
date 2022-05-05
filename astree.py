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

    def __hash__(self):
        hash(str(self))


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
    def __init__(self, token: Token, value: str):
        self._token = token
        self.value = value

    def __str__(self) -> str:
        return self.value

    def token(self) -> Token:
        return self._token


class LetStatement(Statement):
    def __init__(self, token: Token, name: Identifier, value: Expression | None):
        self._token = token
        self.name = name
        self.value = value

    def token(self) -> Token:
        return self._token

    def __str__(self) -> str:
        return f"{self.token_literal()} {self.name} = {self.value}"


class ExpressionStatement(Statement):
    def __init__(self, token: Token, expression: Expression | None):
        self._token = token
        self.expression = expression

    def token(self) -> Token:
        return self._token

    def __str__(self) -> str:
        return str(self.expression)


class Program(Node):
    def __init__(self, statements: list[Statement]):
        self.statements = statements

    def token_literal(self) -> str:
        return "" if len(self.statements) == 0 else self.statements[0].token_literal()

    def __str__(self) -> str:
        return "".join((str(statement) for statement in self.statements))


class LiteralExpression(Expression):
    def __init__(self, token: Token, value):
        self._token = token
        self.value = value

    def token(self) -> Token:
        return self._token

    def __str__(self) -> str:
        return self.token().literal


class IntegerLiteral(LiteralExpression):
    pass


class BooleanLiteral(LiteralExpression):
    pass


class ReturnStatement(Statement):
    def __init__(self, token: Token, return_value: Expression | None):
        self._token = token
        self.return_value = return_value

    def token(self) -> Token:
        return self._token

    def __str__(self) -> str:
        return f"{self.token_literal()} {self._return_value}"


class PrefixExpression(Expression):
    def __init__(self, token: Token, operator: str, right: Expression | None):
        self._token = token
        self.operator = operator
        self.right = right

    def token(self) -> Token:
        return self._token

    def __str__(self) -> str:
        return f"({self.operator}{self.right})"


class InfixExpression(Expression):
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


class CallExpression(Expression):
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


class ArrayLiteral(Expression):
    def __init__(self, token: Token, elements: list[Expression | None] | None):
        self._token = token
        self.elements = elements

    def token(self) -> Token:
        return self._token

    def __str__(self) -> str:
        return f'[{", ".join(str(element) for element in self.elements)}]'


class IndexExpression(Expression):
    def __init__(self, token: Token, left: Expression | None, index: Expression | None):
        self._token = token
        self.left = left
        self.index = index

    def token(self) -> Token:
        return self._token

    def __str__(self) -> str:
        return f"({self.left}[{self.index}])"


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


class FunctionLiteral(Expression):
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


class StringLiteral(Expression):
    def __init__(self, token: Token, value: str):
        self._token = token
        self.value = value

    def token(self) -> Token:
        return self._token

    def __str__(self) -> str:
        return self.value

    def __hash__(self):
        return super.__hash__(self)


class HashLiteral(Expression):
    def __init__(self, token: Token, pairs: dict[Expression, Expression]):
        self._token = token
        self.pairs = pairs

    def token(self) -> Token:
        return self._token

    def __str__(self) -> str:
        return "{{0}}".format(
            ", ".join(f"{key}:{self.pairs[key]}" for key in self.pairs.keys())
        )
