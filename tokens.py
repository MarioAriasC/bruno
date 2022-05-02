from enum import Enum
from typing import NamedTuple


class TokenType(Enum):
    ILLEGAL = "ILLEGAL"
    EOF = "EOF"
    ASSIGN = "="
    EQ = "=="
    NOT_EQ = "!="
    IDENT = "IDENT"
    INT = "INT"
    PLUS = "+"
    COMMA = ","
    SEMICOLON = ";"
    COLON = ":"
    MINUS = "-"
    BANG = "!"
    SLASH = "/"
    ASTERISK = "*"
    LT = "<"
    GT = ">"
    LPAREN = "("
    RPAREN = ")"
    LBRACE = "{"
    RBRACE = "}"
    LBRACKET = "["
    RBRACKET = "]"
    FUNCTION = "FUNCTION"
    LET = "LET"
    TRUE = "TRUE"
    FALSE = "FALSE"
    IF = "IF"
    ELSE = "ELSE"
    RETURN = "RETURN"
    STRING = "STRING"

    def __repr__(self):
        return f'<{self.__class__.__name__}.{self.name}>'


KEYWORDS = {
    'fn': TokenType.FUNCTION,
    'let': TokenType.LET,
    'true': TokenType.TRUE,
    'false': TokenType.FALSE,
    'if': TokenType.IF,
    'else': TokenType.ELSE,
    'return': TokenType.RETURN,
}


def lookup_ident(value: str) -> TokenType:
    try:
        return KEYWORDS[value]
    except KeyError:
        return TokenType.IDENT


class Token(NamedTuple):
    token_type: TokenType
    literal: str
