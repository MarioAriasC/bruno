from lexer import Lexer
from parser import Parser
from astree import IntegerLiteral


def count_statements(i, program):
    size = len(program.statements)
    assert i == size


def assert_let_statement(statement, expected_identifier):
    assert "let" == statement.token_literal()
    assert expected_identifier == statement.name.value
    assert expected_identifier == statement.name.token_literal()


def assert_integer_literal(expression, expected_value):
    assert expected_value == expression.value
    assert str(expected_value) == expression.token_literal()


def assert_identifier(expression, expected_value):
    assert expected_value == expression.value
    assert expected_value == expression.token_literal()


def assert_boolean(expression, expected_value):
    assert expected_value == expression.value
    assert str(expected_value).lower() == expression.token_literal()


def assert_literal_expression(value, expected_value):
    if isinstance(expected_value, bool):
        assert_boolean(value, expected_value)
    elif isinstance(expected_value, int):
        assert_integer_literal(value, expected_value)
    elif isinstance(expected_value, str):
        assert_identifier(value, expected_value)
    else:
        raise AssertionError(f"type of value not handled. got={type(expected_value)!r}")


def test_let_statements():
    tests = [
        ("let x = 5;", "x", 5),
        ("let y = true;", "y", True),
        ("let foobar = y;", "foobar", "y"),
    ]

    for input_source, expected_identifier, expected_value in tests:
        program = create_program(input_source)
        count_statements(1, program)
        statement = program.statements[0]
        assert_let_statement(statement, expected_identifier)
        value = statement.value
        assert_literal_expression(value, expected_value)


def test_return_statement():
    tests = [("return 5;", 5), ("return true;", True), ("return foobar;", "foobar")]

    for input_source, expected_value in tests:
        program = create_program(input_source)
        count_statements(1, program)
        statement = program.statements[0]
        assert "return" == statement.token_literal()
        assert_literal_expression(statement.return_value, expected_value)


def test_identifier_expression():
    input_source = "foobar;"
    program = create_program(input_source)
    count_statements(1, program)
    statement = program.statements[0]
    identifier = statement.expression
    assert "foobar" == identifier.value
    assert "foobar" == identifier.token_literal()


def test_integer_literals():
    input_source = "5;"
    program = create_program(input_source)
    count_statements(1, program)
    statement = program.statements[0]
    literal = statement.expression
    match literal:
        case IntegerLiteral():
            assert 5 == literal.value
            assert "5" == literal.token_literal()
        case _:
            raise AssertionError(
                f"statement.expression not IntegerLiteral. got{type(literal)}"
            )


def test_parsing_prefix_expressions():
    tests = [
        ("!5;", "!", 5),
        ("-15;", "-", 15),
        ("!true;", "!", True),
        ("!false;", "!", False),
    ]

    for input_source, operator, value in tests:
        program = create_program(input_source)
        count_statements(1, program)
        statement = program.statements[0]
        expression = statement.expression
        assert operator == expression.operator
        assert_literal_expression(expression.right, value)


def assert_infix_expression(expression, left_value, operator, right_value):
    assert_literal_expression(expression.left, left_value)
    assert operator == expression.operator
    assert_literal_expression(expression.right, right_value)


def test_parsing_infix_expressions():
    tests = [
        ("5 + 5;", 5, "+", 5),
        ("5 - 5;", 5, "-", 5),
        ("5 * 5;", 5, "*", 5),
        ("5 / 5;", 5, "/", 5),
        ("5 > 5;", 5, ">", 5),
        ("5 < 5;", 5, "<", 5),
        ("5 == 5;", 5, "==", 5),
        ("5 != 5;", 5, "!=", 5),
        ("true == true", True, "==", True),
        ("true != false", True, "!=", False),
        ("false == false", False, "==", False),
    ]

    for input_source, left_value, operator, right_value in tests:
        program = create_program(input_source)
        count_statements(1, program)
        assert_infix_expression(
            program.statements[0].expression, left_value, operator, right_value
        )


def test_operator_precedence():
    tests = [
        (
            "-a * b",
            "((-a) * b)",
        ),
        (
            "!-a",
            "(!(-a))",
        ),
        (
            "a + b + c",
            "((a + b) + c)",
        ),
        (
            "a + b - c",
            "((a + b) - c)",
        ),
        (
            "a * b * c",
            "((a * b) * c)",
        ),
        (
            "a * b / c",
            "((a * b) / c)",
        ),
        (
            "a + b / c",
            "(a + (b / c))",
        ),
        (
            "a + b * c + d / e - f",
            "(((a + (b * c)) + (d / e)) - f)",
        ),
        (
            "3 + 4; -5 * 5",
            "(3 + 4)((-5) * 5)",
        ),
        (
            "5 > 4 == 3 < 4",
            "((5 > 4) == (3 < 4))",
        ),
        (
            "5 < 4 != 3 > 4",
            "((5 < 4) != (3 > 4))",
        ),
        (
            "3 + 4 * 5 == 3 * 1 + 4 * 5",
            "((3 + (4 * 5)) == ((3 * 1) + (4 * 5)))",
        ),
        (
            "true",
            "true",
        ),
        (
            "false",
            "false",
        ),
        (
            "3 > 5 == false",
            "((3 > 5) == false)",
        ),
        (
            "3 < 5 == true",
            "((3 < 5) == true)",
        ),
        (
            "1 + (2 + 3) + 4",
            "((1 + (2 + 3)) + 4)",
        ),
        (
            "(5 + 5) * 2",
            "((5 + 5) * 2)",
        ),
        (
            "2 / (5 + 5)",
            "(2 / (5 + 5))",
        ),
        (
            "(5 + 5) * 2 * (5 + 5)",
            "(((5 + 5) * 2) * (5 + 5))",
        ),
        (
            "-(5 + 5)",
            "(-(5 + 5))",
        ),
        (
            "!(true == true)",
            "(!(true == true))",
        ),
        (
            "a + add(b * c) + d",
            "((a + add((b * c))) + d)",
        ),
        (
            "add(a, b, 1, 2 * 3, 4 + 5, add(6, 7 * 8))",
            "add(a, b, 1, (2 * 3), (4 + 5), add(6, (7 * 8)))",
        ),
        (
            "add(a + b + c * d / f + g)",
            "add((((a + b) + ((c * d) / f)) + g))",
        ),
        (
            "a * [1, 2, 3, 4][b * c] * d",
            "((a * ([1, 2, 3, 4][(b * c)])) * d)",
        ),
        (
            "add(a * b[2], b[1], 2 * [1, 2][1])",
            "add((a * (b[2])), (b[1]), (2 * ([1, 2][1])))",
        ),
    ]

    for input_source, expected in tests:
        program = create_program(input_source)
        actual = str(program)
        assert expected == actual


def test_boolean_expression():
    tests = [("true", True), ("false", False)]

    for input_source, expected_boolean in tests:
        program = create_program(input_source)
        count_statements(1, program)
        boolean_literal = program.statements[0].expression
        assert expected_boolean == boolean_literal.value


def test_if_expression():
    input_source = "if (x < y) { x }"
    exp = assert_if_expression(input_source)
    assert exp.alternative is None


def assert_if_expression(input_source):
    program = create_program(input_source)
    count_statements(1, program)
    exp = program.statements[0].expression
    assert_infix_expression(exp.condition, "x", "<", "y")
    assert 1 == len(exp.consequence.statements)
    consequence = exp.consequence.statements[0]
    assert_identifier(consequence.expression, "x")
    return exp


def test_if_else_expression():
    input_source = "if (x < y) { x } else { y }"
    exp = assert_if_expression(input_source)
    assert 1 == len(exp.alternative.statements)
    alternative = exp.alternative.statements[0]
    assert_identifier(alternative.expression, "y")


def test_function_literal_parsing():
    input_source = "fn(x, y) { x + y;}"
    program = create_program(input_source)
    count_statements(1, program)
    function = program.statements[0].expression
    assert_literal_expression(function.parameters[0], "x")
    assert_literal_expression(function.parameters[1], "y")
    assert 1 == len(function.body.statements)
    assert_infix_expression(function.body.statements[0].expression, "x", "+", "y")


def test_function_parameter_parsing():
    tests = [("fn() {}", []), ("fn(x) {}", ["x"]), ("fn(x, y, z) {}", ["x", "y", "z"])]

    for input_source, expected_params in tests:
        program = create_program(input_source)
        function = program.statements[0].expression
        assert len(expected_params) == len(function.parameters)
        for i, param in enumerate(expected_params):
            assert_literal_expression(function.parameters[i], param)


def test_call_expression_parsing():
    input_source = "add(1, 2 * 3, 4+5)"
    program = create_program(input_source)
    count_statements(1, program)
    exp = program.statements[0].expression
    assert_identifier(exp.function, "add")
    assert 3 == len(exp.arguments)
    assert_literal_expression(exp.arguments[0], 1)
    assert_infix_expression(exp.arguments[1], 2, "*", 3)
    assert_infix_expression(exp.arguments[2], 4, "+", 5)


def test_literal_expression():
    input_source = '"hello world";'
    program = create_program(input_source)
    count_statements(1, program)
    assert "hello world" == program.statements[0].expression.value


def test_parsing_array_literal():
    input_source = "[1, 2 * 2, 3 + 3]"
    program = create_program(input_source)
    array = program.statements[0].expression
    assert_integer_literal(array.elements[0], 1)
    assert_infix_expression(array.elements[1], 2, "*", 2)
    assert_infix_expression(array.elements[2], 3, "+", 3)


def test_parsing_index_expression():
    input_source = "myArray[1 + 1]"
    program = create_program(input_source)
    index = program.statements[0].expression
    assert_identifier(index.left, "myArray")
    assert_infix_expression(index.index, 1, "+", 1)


def test_hash_string_keys():
    input_source = '{"one": 1, "two": 2, "three": 3}'
    program = create_program(input_source)
    hash_literal = program.statements[0].expression
    assert 3 == len(hash_literal.pairs)
    expected = {"one": 1, "two": 2, "three": 3}
    for key, value in hash_literal.pairs.items():
        expected_value = expected[str(key)]
        assert_literal_expression(value, expected_value)


def check_parser_errors(parser):
    errors = parser.errors()
    if len(errors) != 0:
        jump = " \n"
        raise AssertionError(f"parser has {len(errors)} errors: \n{jump.join(errors)}")


def create_program(input_source):
    lexer = Lexer(input_source)
    parser = Parser(lexer)
    program = parser.parse_program()
    check_parser_errors(parser)
    return program
