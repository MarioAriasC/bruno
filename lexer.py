from tokens import Token, TokenType, lookup_ident


def _is_identifier(char):
    return char.isalpha() or char == '_'


class Lexer:
    ZERO = ''
    WHITE_SPACES = (' ', '\t', '\n', '\r')

    def __init__(self, input_source):
        self._input = input_source
        self._position = 0
        self._read_position = 0
        self._ch = Lexer.ZERO
        self._read_char()

    def _read_char(self):
        self._ch = self._peak_char()
        self._position = self._read_position
        self._read_position = self._read_position + 1

    def next_token(self) -> Token:
        def ends_with_equal(one_char: TokenType, two_chars: TokenType, duplicate_chars=True) -> Token:
            if self._peak_char() != '=':
                return self._token(one_char)
            current_char = self._ch
            self._read_char()
            value = f'{current_char}{current_char}' if duplicate_chars else f'{current_char}{self._ch}'
            return Token(two_chars, value)

        self._skip_whitespace()

        match self._ch:
            case '=':
                r = ends_with_equal(TokenType.ASSIGN, TokenType.EQ)
            case ';':
                r = self._token(TokenType.SEMICOLON)
            case ':':
                r = self._token(TokenType.COLON)
            case ',':
                r = self._token(TokenType.COMMA)
            case '(':
                r = self._token(TokenType.LPAREN)
            case ')':
                r = self._token(TokenType.RPAREN)
            case '{':
                r = self._token(TokenType.LBRACE)
            case '}':
                r = self._token(TokenType.RBRACE)
            case '[':
                r = self._token(TokenType.LBRACKET)
            case ']':
                r = self._token(TokenType.RBRACKET)
            case '+':
                r = self._token(TokenType.PLUS)
            case '-':
                r = self._token(TokenType.MINUS)
            case '*':
                r = self._token(TokenType.ASTERISK)
            case '/':
                r = self._token(TokenType.SLASH)
            case '<':
                r = self._token(TokenType.LT)
            case '>':
                r = self._token(TokenType.GT)
            case '!':
                r = ends_with_equal(TokenType.BANG, TokenType.NOT_EQ, duplicate_chars=False)
            case Lexer.ZERO:
                r = Token(TokenType.EOF, "")
            case '"':
                r = Token(TokenType.STRING, self._read_string())
            case _:
                if _is_identifier(self._ch):
                    identifier = self._read_identifier()
                    return Token(lookup_ident(identifier), identifier)
                elif self._ch.isdigit():
                    return Token(TokenType.INT, self._read_number())
                else:
                    return Token(TokenType.ILLEGAL, self._ch)
        self._read_char()
        return r

    def _peak_char(self):
        return Lexer.ZERO if self._read_position >= len(self._input) else self._input[self._read_position]

    def _token(self, token_type):
        return Token(token_type, self._ch)

    def _skip_whitespace(self):
        while self._ch in Lexer.WHITE_SPACES:
            self._read_char()

    def _read_value(self, predicate) -> str:
        current_position = self._position
        while predicate(self._ch):
            self._read_char()
        return self._input[current_position:self._position]

    def _read_identifier(self):
        return self._read_value(lambda ch: _is_identifier(ch))

    def _read_number(self):
        return self._read_value(lambda ch: ch.isdigit())

    def _read_string(self):
        start = self._position + 1
        while True:
            self._read_char()
            if self._ch in ['"', Lexer.ZERO]:
                break

        return self._input[start:self._position]
