from evaluator import evaluate, Environment
from objects import MInteger, MBoolean, NULL, MString, TRUE, FALSE
from test_parser import create_program


def _eval(input_source):
    program = create_program(input_source)
    return evaluate(program, Environment())


def assert_integer_object(evaluated, expected):
    match evaluated:
        case MInteger():
            assert expected == evaluated.value
        case _:
            raise AssertionError(
                f"obj is not MInteger, got {type(evaluated)}, {evaluated}"
            )


def assert_integer(input_source, expected):
    evaluated = _eval(input_source)
    assert_integer_object(evaluated, expected)


def test_eval_integer_expressions():
    tests = [
        ("5", 5),
        ("10", 10),
        ("-5", -5),
        ("-10", -10),
        ("5 + 5 + 5 + 5 - 10", 10),
        ("2 * 2 * 2 * 2 * 2", 32),
        ("-50 + 100 + -50", 0),
        ("5 * 2 + 10", 20),
        ("5 + 2 * 10", 25),
        ("20 + 2 * -10", 0),
        ("50 / 2 * 2 + 10", 60),
        ("2 * (5 + 10)", 30),
        ("3 * 3 * 3 + 10", 37),
        ("3 * (3 * 3) + 10", 37),
        ("(5 + 10 * 2 + 15 / 3) * 2 + -10", 50),
    ]

    for input_source, expected in tests:
        assert_integer(input_source, expected)


def assert_boolean(input_source, expected):
    evaluated = _eval(input_source)
    match evaluated:
        case MBoolean(value):
            assert expected == value
        case _:
            raise AssertionError(
                f"obj is not MBoolean, got {type(evaluated)}, {evaluated}"
            )


def test_eval_boolean_expression():
    tests = [
        ("true", True),
        ("false", False),
        ("1 < 2", True),
        ("1 > 2", False),
        ("1 < 1", False),
        ("1 > 1", False),
        ("1 == 1", True),
        ("1 != 1", False),
        ("1 == 2", False),
        ("1 != 2", True),
        ("true == true", True),
        ("false == false", True),
        ("true == false", False),
        ("true != false", True),
        ("false != true", True),
        ("(1 < 2) == true", True),
        ("(1 < 2) == false", False),
        ("(1 > 2) == true", False),
        ("(1 > 2) == false", True),
    ]

    for input_source, expected in tests:
        assert_boolean(input_source, expected)


def test_bang_operator():
    tests = [
        ("!true", False),
        ("!false", True),
        ("!5", False),
        ("!!true", True),
        ("!!false", False),
        ("!!5", True),
    ]

    for input_source, expected in tests:
        assert_boolean(input_source, expected)


def assert_none_object(obj):
    assert NULL is obj


def test_if_else_expression():
    tests = [
        ("if (true) { 10 }", 10),
        ("if (false) { 10 }", None),
        ("if (1) { 10 }", 10),
        ("if (1 < 2) { 10 }", 10),
        ("if (1 > 2) { 10 }", None),
        ("if (1 > 2) { 10 } else { 20 }", 20),
        ("if (1 < 2) { 10 } else { 20 }", 10),
    ]

    for input_source, expected in tests:
        evaluated = _eval(input_source)
        if expected is None:
            assert_none_object(evaluated)
        else:
            assert_integer_object(evaluated, expected)


def test_return_statement():
    tests = [
        ("return 10;", 10),
        ("return 10; 9;", 10),
        ("return 2 * 5; 9;", 10),
        ("9; return 2 * 5; 9;", 10),
        (
            """if (10 > 1) {
            if (10 > 1) {
            return 10;
            }
        
            return 1;
            }""",
            10,
        ),
        (
            """let f = fn(x) {
                return x;
                x + 10;
            
            };
            f(10);
            """,
            10,
        ),
        (
            """let f = fn(x) {
            let
            result = x + 10;
            return result;
            return 10;
            };
            f(10);
            """,
            20,
        ),
    ]

    for input_source, expected in tests:
        assert_integer(input_source, expected)


def test_error_handling():
    tests = [
        ("5 + true;", "type mismatch: MInteger + MBoolean"),
        ("5 + true; 5;", "type mismatch: MInteger + MBoolean"),
        ("-true", "unknown operator: -MBoolean"),
        ("true + false;", "unknown operator: MBoolean + MBoolean"),
        ("true + false + true + false;", "unknown operator: MBoolean + MBoolean"),
        ("5; true + false; 5", "unknown operator: MBoolean + MBoolean"),
        ("if (10 > 1) { true + false; }", "unknown operator: MBoolean + MBoolean"),
        (
            """
            if (10 > 1) {
            if (10 > 1) {
            return true + false;
            }
            
            return 1;}""",
            "unknown operator: MBoolean + MBoolean",
        ),
        ("foobar", "identifier not found: foobar"),
        ('("Hello" - "World")', "unknown operator: MString - MString"),
        ('{"name": "Monkey"}[fn(x) {x}];', "unusable as a hash key: MFunction"),
    ]

    for input_source, expected in tests:
        error = _eval(input_source)
        assert expected == error.message


def test_let_statement():
    tests = [
        ("let a = 5; a;", 5),
        ("let a = 5 * 5; a;", 25),
        ("let a = 5; let b = a; b;", 5),
        ("let a = 5; let b = a; let c = a + b + 5; c;", 15),
    ]

    for input_source, expected in tests:
        assert_integer(input_source, expected)


def test_function_object():
    input_source = "fn(x) { x + 2; };"
    fn = _eval(input_source)
    parameters = fn.parameters
    assert 1 == len(parameters)
    assert "x" == str(parameters[0])
    assert "(x + 2)" == str(fn.body)


def test_function_application():
    tests = [
        ("let identity = fn(x) { x; }; identity(5);", 5),
        ("let identity = fn(x) { return x; }; identity(5);", 5),
        ("let double = fn(x) { x * 2; }; double(5);", 10),
        ("let add = fn(x, y) { x + y; }; add(5, 5);", 10),
        ("let add = fn(x, y) { x + y; }; add(5 + 5, add(5, 5));", 20),
        ("fn(x) { x; }(5)", 5),
    ]

    for input_source, expected in tests:
        assert_integer(input_source, expected)


def test_enclosing_environments():
    input_source = """let first = 10;
    let second = 10;
    let third = 10;

    let ourFunction = fn(first) {
      let second = 20;

      first + second + third;
    };

    ourFunction(20) + first + second;
    """
    assert_integer_object(_eval(input_source), 70)


def assert_string(input_source, expected):
    evaluated = _eval(input_source)
    match evaluated:
        case MString(value):
            assert expected == value
        case _:
            raise AssertionError(
                f"obj is not MString, got {type(evaluated)}, {evaluated}"
            )


def test_string_literal():
    assert_string('"Hello World!"', "Hello World!")


def test_string_concatenation():
    assert_string('"Hello" + " " + "World!"', "Hello World!")


def test_builtin_functions():
    tests = [
        ('len("")', 0),
        ('len("four")', 4),
        ('len("hello world")', 11),
        ("len(1)", "argument to `len` not supported, got MInteger"),
        ('len("one", "two")', "wrong number of arguments. got=2, want=1"),
        ("len([1, 2, 3])", 3),
        ("len([])", 0),
        ("push([], 1)", [1]),
        ("push(1, 1)", "argument to `push` must be ARRAY, got MInteger"),
        ("first([1, 2, 3])", 1),
        ("first([])", None),
        ("first(1)", "argument to `first` must be ARRAY, got MInteger"),
        ("last([1, 2, 3])", 3),
        ("last([])", None),
        ("last(1)", "argument to `last` must be ARRAY, got MInteger"),
        ("rest([1, 2, 3])", [2, 3]),
        ("rest([])", None),
    ]

    for input_source, expected in tests:
        evaluated = _eval(input_source)
        if expected is None:
            assert_none_object(evaluated)
        elif isinstance(expected, int):
            assert_integer_object(evaluated, expected)
        elif isinstance(expected, str):
            assert expected == evaluated.message
        else:
            assert len(expected) == len(evaluated.elements)
            for i, element in enumerate(expected):
                assert_integer_object(evaluated.elements[i], element)


def test_array_literal():
    result = _eval("[1, 2 * 2, 3 + 3]")
    assert 3 == len(result.elements)
    for i, value in enumerate([1, 4, 6]):
        assert_integer_object(result.elements[i], value)


def test_array_index_expression():
    tests = [
        ("[1, 2, 3][0]", 1),
        ("[1, 2, 3][1]", 2),
        ("[1, 2, 3][2]", 3),
        ("let i = 0; [1][i];", 1),
        ("[1, 2, 3][1 + 1];", 3),
        ("let myArray = [1, 2, 3]; myArray[2];", 3),
        ("let myArray = [1, 2, 3]; myArray[0] + myArray[1] + myArray[2];", 6),
        ("let myArray = [1, 2, 3]; let i = myArray[0]; myArray[i]", 2),
        ("[1, 2, 3][3]", None),
        ("[1, 2, 3][-1]", None),
    ]

    for input_source, expected in tests:
        evaluated = _eval(input_source)
        if isinstance(expected, int):
            assert_integer_object(evaluated, expected)
        else:
            assert_none_object(evaluated)


def test_hash_literal():
    input_source = """let two = "two";
    {
    "one": 10 - 9,
    two: 1 + 1,
    "thr" + "ee": 6 / 2,
    4: 4,
    true: 5,
    false: 6
    }"""

    result = _eval(input_source)
    expected = {
        MString("one").hash_key(): 1,
        MString("two").hash_key(): 2,
        MString("three").hash_key(): 3,
        MInteger(4).hash_key(): 4,
        TRUE.hash_key(): 5,
        FALSE.hash_key(): 6,
    }
    assert 6 == len(expected)
    assert len(result.pairs) == len(expected)
    for expected_key, expected_value in expected.items():
        pair = result.pairs[expected_key]
        assert pair is not None
        assert_integer_object(pair.value, expected_value)


def test_hash_index_expression():
    tests = [
        ('{"foo": 5, "bar": 7}["foo"]', 5),
        ('{"foo": 5}["bar"]', None),
        ('let key = "foo";{"foo": 5}[key]', 5),
        ('{}["foo"]', None),
        ("{5:5}[5]", 5),
        ("{true:5}[true]", 5),
        ("{false:5}[false]", 5),
    ]

    for input_source, expected in tests:
        print(f"input_source = {input_source}")
        evaluated = _eval(input_source)
        if isinstance(expected, int):
            assert_integer_object(evaluated, expected)
        else:
            assert_none_object(evaluated)


def test_recursive_fibonacci():
    input_source = """let fibonacci = fn(x) {
	if (x == 0) {
		return 0;
	} else {
		if (x == 1) {
			return 1;
		} else {
			fibonacci(x - 1) + fibonacci(x - 2);
		}
	}
};
fibonacci(15);
    """
    evaluated = _eval(input_source)
    assert_integer_object(evaluated, 610)
