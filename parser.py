from enum import auto, IntEnum

from astree import (
    Identifier,
    LetStatement,
    ExpressionStatement,
    Program,
    IntegerLiteral,
    BooleanLiteral,
    ReturnStatement,
    PrefixExpression,
    Expression,
    InfixExpression,
    CallExpression,
    ArrayLiteral,
    IndexExpression,
    BlockStatement,
    IfExpression,
    FunctionLiteral,
    StringLiteral,
    HashLiteral,
)
from lexer import Lexer
from tokens import TokenType, Token
from utils import nn


class Precedence(IntEnum):
    LOWEST = auto()
    EQUALS = auto()
    LESS_GREATER = auto()
    SUM = auto()
    PRODUCT = auto()
    PREFIX = auto()
    CALL = auto()
    INDEX = auto()


class Parser:
    def __init__(self, lexer: Lexer):
        self._lexer = lexer
        self._cur_token: Token | None = None
        self._peek_token: Token | None = None
        self._errors:list[str] = []
        self._prefix_parsers = {
            TokenType.INT: self._parse_integer_literal,
            TokenType.TRUE: self._parse_boolean_literal,
            TokenType.FALSE: self._parse_boolean_literal,
            TokenType.IDENT: self._parse_identifier,
            TokenType.BANG: self._parse_prefix_expression,
            TokenType.MINUS: self._parse_prefix_expression,
            TokenType.LPAREN: self._parse_group_expression,
            TokenType.LBRACKET: self._parse_array_literal,
            TokenType.IF: self._parse_if_expression,
            TokenType.FUNCTION: self._parse_function_literal,
            TokenType.STRING: self._parse_string_literal,
            TokenType.LBRACE: self._parse_hash_literal,
        }
        self._infix_parsers = {
            TokenType.PLUS: self._parse_infix_expression,
            TokenType.MINUS: self._parse_infix_expression,
            TokenType.SLASH: self._parse_infix_expression,
            TokenType.ASTERISK: self._parse_infix_expression,
            TokenType.EQ: self._parse_infix_expression,
            TokenType.NOT_EQ: self._parse_infix_expression,
            TokenType.LT: self._parse_infix_expression,
            TokenType.GT: self._parse_infix_expression,
            TokenType.LPAREN: self._parse_call_expression,
            TokenType.LBRACKET: self._parse_index_expression,
        }
        self._next_token()
        self._next_token()
        self._precedences = {
            TokenType.EQ: Precedence.EQUALS,
            TokenType.NOT_EQ: Precedence.EQUALS,
            TokenType.LT: Precedence.LESS_GREATER,
            TokenType.GT: Precedence.LESS_GREATER,
            TokenType.PLUS: Precedence.SUM,
            TokenType.MINUS: Precedence.SUM,
            TokenType.SLASH: Precedence.PRODUCT,
            TokenType.ASTERISK: Precedence.PRODUCT,
            TokenType.LPAREN: Precedence.CALL,
            TokenType.LBRACKET: Precedence.INDEX,
        }

    def errors(self):
        return self._errors

    def parse_program(self):
        # print("parse_program")
        statements = []
        while self._cur_token.token_type != TokenType.EOF:
            statement = self._parse_statement()
            # print(f"statement = {statement}")
            if statement is not None:
                statements.append(statement)
            self._next_token()

        return Program(statements)

    def _parse_statement(self):
        # print("_parse_statement")
        match self._cur_token.token_type:
            case TokenType.LET:
                return self._parse_let_statement()
            case TokenType.RETURN:
                return self._parse_return_statement()
            case _:
                return self._parse_expression_statement()

    def _next_token(self):
        # print("_next_token")
        self._cur_token = self._peek_token
        self._peek_token = self._lexer.next_token()

    def _parse_let_statement(self):
        # print("_parse_let_statement")
        token = self._cur_token
        if not self._expect_peek(TokenType.IDENT):
            return None

        name = Identifier(self._cur_token, self._cur_token.literal)

        if not self._expect_peek(TokenType.ASSIGN):
            return None

        self._next_token()

        value = self._parse_expression(Precedence.LOWEST)

        if self._peek_token_is(TokenType.SEMICOLON):
            self._next_token()

        return LetStatement(token, name, value)

    def _expect_peek(self, token_type):
        # print("_expect_peek")
        if self._peek_token_is(token_type):
            self._next_token()
            return True

        self._peek_error(token_type)
        return False

    def _peek_token_is(self, token_type):
        # print("_peek_token_is")
        return self._peek_token.token_type == token_type

    def _parse_expression(self, precedence):
        # print("_parse_expression")
        prefix = self._prefix_parsers.get(self._cur_token.token_type, None)
        if prefix is None:
            self._no_prefix_parser_error(self._cur_token.token_type)
            return None

        left = prefix()

        while (
            not self._peek_token_is(TokenType.SEMICOLON)
            and precedence < self._peek_precedence()
        ):
            infix = self._infix_parsers.get(self._peek_token.token_type, None)
            if infix is None:
                return left

            self._next_token()
            left = infix(left)

        return left

    def _no_prefix_parser_error(self, token_type):
        # print("_no_prefix_parser_error")
        self._errors.append(f"no prefix parser for {token_type} function")

    def _parse_expression_statement(self):
        # print("_parse_expression_statement")
        token = self._cur_token
        expression = self._parse_expression(Precedence.LOWEST)
        if self._peek_token_is(TokenType.SEMICOLON):
            self._next_token()

        return ExpressionStatement(token, expression)

    def _parse_integer_literal(self):
        token = self._cur_token
        try:
            value = int(token.literal)
            return IntegerLiteral(token, value)
        except ValueError:
            self._errors.append(f"could not parse {token.literal} as integer")
            return None

    def _parse_boolean_literal(self):
        return BooleanLiteral(self._cur_token, self._cur_token_is(TokenType.TRUE))

    def _cur_token_is(self, token_type):
        return self._cur_token.token_type == token_type

    def _parse_identifier(self):
        return Identifier(self._cur_token, self._cur_token.literal)

    def _parse_return_statement(self):
        token = self._cur_token
        self._next_token()
        return_value = self._parse_expression(Precedence.LOWEST)

        while self._peek_token_is(TokenType.SEMICOLON):
            self._next_token()

        return ReturnStatement(token, return_value)

    def _parse_prefix_expression(self):
        token = self._cur_token
        operator = token.literal
        self._next_token()

        right = self._parse_expression(Precedence.PREFIX)
        # print(f"parsePrefixExpression {token} {operator} {right}")
        return PrefixExpression(token, operator, right)

    def _parse_infix_expression(self, left: Expression | None):
        token = nn(self._cur_token)
        operator = token.literal
        precedence = self._cur_precedence()
        self._next_token()
        right = self._parse_expression(precedence)
        return InfixExpression(token, left, operator, right)

    def _parse_call_expression(self, expression: Expression | None):
        token = nn(self._cur_token)
        arguments = self._parse_expression_list(TokenType.RPAREN)
        return CallExpression(token, expression, arguments)

    def _parse_group_expression(self):
        self._next_token()
        exp = self._parse_expression(Precedence.LOWEST)
        return exp if self._expect_peek(TokenType.RPAREN) else None

    def _peek_precedence(self):
        return self._find_precedence(self._peek_token.token_type)

    def _find_precedence(self, token_type) -> Precedence:
        return self._precedences.get(token_type, Precedence.LOWEST)

    def _cur_precedence(self):
        return self._find_precedence(self._cur_token.token_type)

    def _parse_expression_list(self, end):
        arguments = []
        if self._peek_token_is(end):
            self._next_token()
            return arguments

        self._next_token()
        arguments.append(self._parse_expression(Precedence.LOWEST))

        while self._peek_token_is(TokenType.COMMA):
            self._next_token()
            self._next_token()
            arguments.append(self._parse_expression(Precedence.LOWEST))

        return arguments if self._expect_peek(end) else None

    def _parse_array_literal(self):
        token = self._cur_token
        return ArrayLiteral(token, self._parse_expression_list(TokenType.RBRACKET))

    def _parse_index_expression(self, left):
        token = self._cur_token
        self._next_token()

        index = self._parse_expression(Precedence.LOWEST)

        return (
            IndexExpression(token, left, index)
            if self._expect_peek(TokenType.RBRACKET)
            else None
        )

    def _parse_if_expression(self):
        token = self._cur_token
        if not self._expect_peek(TokenType.LPAREN):
            return None

        self._next_token()
        condition = self._parse_expression(Precedence.LOWEST)
        if not self._expect_peek(TokenType.RPAREN):
            return None

        if not self._expect_peek(TokenType.LBRACE):
            return None

        consequence = self._parse_block_statement()

        if self._peek_token_is(TokenType.ELSE):
            self._next_token()
            if not self._expect_peek(TokenType.LBRACE):
                return None
            alternative = self._parse_block_statement()
        else:
            alternative = None

        return IfExpression(token, condition, consequence, alternative)

    def _parse_block_statement(self):
        token = self._cur_token
        statements = []
        self._next_token()

        while not self._cur_token_is(TokenType.RBRACE) and not self._cur_token_is(
            TokenType.EOF
        ):
            statement = self._parse_statement()
            if statement is not None:
                statements.append(statement)
            self._next_token()

        return BlockStatement(token, statements)

    def _parse_function_literal(self):
        token = self._cur_token
        if not self._expect_peek(TokenType.LPAREN):
            return None

        parameters = self._parse_function_parameters()

        if not self._expect_peek(TokenType.LBRACE):
            return None

        body = self._parse_block_statement()
        return FunctionLiteral(token, parameters, body)

    def _peek_error(self, token_type):
        self._errors.append(
            f"Expected next token to be {token_type}, got {self._peek_token.token_type} instead"
        )

    def _parse_function_parameters(self):
        parameters = []
        if self._peek_token_is(TokenType.RPAREN):
            self._next_token()
            return parameters

        self._next_token()
        token = self._cur_token

        parameters.append(Identifier(token, token.literal))

        while self._peek_token_is(TokenType.COMMA):
            self._next_token()
            self._next_token()
            inner_token = self._cur_token
            parameters.append(Identifier(inner_token, inner_token.literal))

        if not self._expect_peek(TokenType.RPAREN):
            return None

        return parameters

    def _parse_string_literal(self):
        return StringLiteral(self._cur_token, self._cur_token.literal)

    def _parse_hash_literal(self):
        token = self._cur_token
        pairs = {}
        while not self._peek_token_is(TokenType.RBRACE):
            self._next_token()
            key = self._parse_expression(Precedence.LOWEST)
            if not self._expect_peek(TokenType.COLON):
                return None

            self._next_token()
            value = self._parse_expression(Precedence.LOWEST)
            pairs[key] = value
            if not self._peek_token_is(TokenType.RBRACE) and not self._expect_peek(
                TokenType.COMMA
            ):
                return None

        return (
            HashLiteral(token, pairs) if self._expect_peek(TokenType.RBRACE) else None
        )
