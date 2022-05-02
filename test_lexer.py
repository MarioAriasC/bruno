from lexer import Lexer
from tokens import TokenType


def test_validate_lexer():
    code = ('let five = 5;\n'
            'let ten = 10;\n'
            '\n'
            'let add = fn(x, y) {\n'
            '	x + y;\n'
            '}\n'
            '\n'
            'let result = add(five, ten);\n'
            '!-/*5;\n'
            '5 < 10 > 5;\n'
            '\n'
            'if (5 < 10) {\n'
            '	return true;\n'
            '} else {\n'
            '	return false;\n'
            '}\n'
            '\n'
            '10 == 10;\n'
            '10 != 9;   \n'
            '"foobar"\n'
            '"foo bar"     \n'
            '[1,2];\n'
            '{"foo":"bar"}')

    lexer = Lexer(code)

    expected = [
        (TokenType.LET, "let"),
        (TokenType.IDENT, "five"),
        (TokenType.ASSIGN, "="),
        (TokenType.INT, "5"),
        (TokenType.SEMICOLON, ";"),
        (TokenType.LET, "let"),
        (TokenType.IDENT, "ten"),
        (TokenType.ASSIGN, "="),
        (TokenType.INT, "10"),
        (TokenType.SEMICOLON, ";"),
        (TokenType.LET, "let"),
        (TokenType.IDENT, "add"),
        (TokenType.ASSIGN, "="),
        (TokenType.FUNCTION, "fn"),
        (TokenType.LPAREN, "("),
        (TokenType.IDENT, "x"),
        (TokenType.COMMA, ","),
        (TokenType.IDENT, "y"),
        (TokenType.RPAREN, ")"),
        (TokenType.LBRACE, "{"),
        (TokenType.IDENT, "x"),
        (TokenType.PLUS, "+"),
        (TokenType.IDENT, "y"),
        (TokenType.SEMICOLON, ";"),
        (TokenType.RBRACE, "}"),
        (TokenType.LET, "let"),
        (TokenType.IDENT, "result"),
        (TokenType.ASSIGN, "="),
        (TokenType.IDENT, "add"),
        (TokenType.LPAREN, "("),
        (TokenType.IDENT, "five"),
        (TokenType.COMMA, ","),
        (TokenType.IDENT, "ten"),
        (TokenType.RPAREN, ")"),
        (TokenType.SEMICOLON, ";"),
        (TokenType.BANG, "!"),
        (TokenType.MINUS, "-"),
        (TokenType.SLASH, "/"),
        (TokenType.ASTERISK, "*"),
        (TokenType.INT, "5"),
        (TokenType.SEMICOLON, ";"),
        (TokenType.INT, "5"),
        (TokenType.LT, "<"),
        (TokenType.INT, "10"),
        (TokenType.GT, ">"),
        (TokenType.INT, "5"),
        (TokenType.SEMICOLON, ";"),
        (TokenType.IF, "if"),
        (TokenType.LPAREN, "("),
        (TokenType.INT, "5"),
        (TokenType.LT, "<"),
        (TokenType.INT, "10"),
        (TokenType.RPAREN, ")"),
        (TokenType.LBRACE, "{"),
        (TokenType.RETURN, "return"),
        (TokenType.TRUE, "true"),
        (TokenType.SEMICOLON, ";"),
        (TokenType.RBRACE, "}"),
        (TokenType.ELSE, "else"),
        (TokenType.LBRACE, "{"),
        (TokenType.RETURN, "return"),
        (TokenType.FALSE, "false"),
        (TokenType.SEMICOLON, ";"),
        (TokenType.RBRACE, "}"),
        (TokenType.INT, "10"),
        (TokenType.EQ, "=="),
        (TokenType.INT, "10"),
        (TokenType.SEMICOLON, ";"),
        (TokenType.INT, "10"),
        (TokenType.NOT_EQ, "!="),
        (TokenType.INT, "9"),
        (TokenType.SEMICOLON, ";"),
        (TokenType.STRING, "foobar"),
        (TokenType.STRING, "foo bar"),
        (TokenType.LBRACKET, "["),
        (TokenType.INT, "1"),
        (TokenType.COMMA, ","),
        (TokenType.INT, "2"),
        (TokenType.RBRACKET, "]"),
        (TokenType.SEMICOLON, ";"),
        (TokenType.LBRACE, "{"),
        (TokenType.STRING, "foo"),
        (TokenType.COLON, ":"),
        (TokenType.STRING, "bar"),
        (TokenType.RBRACE, "}"),
        (TokenType.EOF, ""),
    ]

    for token_type, literal in expected:
        token = lexer.next_token()
        assert token.token_type == token_type
        assert token.literal == literal
