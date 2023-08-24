from typing import cast

from astree import (
    Program,
    IntegerLiteral,
    ExpressionStatement,
    PrefixExpression,
    InfixExpression,
    BooleanLiteral,
    IfExpression,
    BlockStatement,
    ReturnStatement,
    CallExpression,
    LetStatement,
    FunctionLiteral,
    Identifier,
    StringLiteral,
    IndexExpression,
    HashLiteral,
    ArrayLiteral, Statement, Expression,
)
from objects import (
    MReturnValue,
    MError,
    MInteger,
    MObject,
    MString,
    TRUE,
    FALSE,
    MBoolean,
    NULL,
    MNull,
    MFunction,
    MBuiltinFunction,
    BUILTINS,
    MArray,
    MHash,
    MValue,
    HashPair,
)
from utils import nn


class Environment:
    def __init__(self, store=None, outer=None):
        self.outer = outer
        self.store = {} if store is None else store

    def __setitem__(self, key, value):
        self.store[key] = value

    def __getitem__(self, key):
        obj = self.store.get(key, None)
        return self.outer[key] if obj is None and self.outer is not None else obj


def _eval_block_statement(block_statement: BlockStatement, env: Environment):
    result = None
    for statement in nn(block_statement.statements):
        result = _evaluate(nn(statement), env)
        match result:
            case MReturnValue():
                return result
            case MError():
                return result
    return result


def _eval_minus_prefix_operator_expression(right):
    if right is None:
        return None

    match right:
        case MInteger():
            return -right
        case _:
            return MError(f"unknown operator: -{right.type_desc()}")


def _eval_bang_operator_expression(right):
    if right is TRUE or right is not FALSE and right is not NULL:
        return FALSE
    # else:
    return TRUE


def _eval_prefix_expression(operator: str, right):
    match operator:
        case "!":
            return _eval_bang_operator_expression(right)
        case "-":
            return _eval_minus_prefix_operator_expression(right)
        case _:
            return MError(f"Unknown operator : {operator}{right.type_desc()}")


def _eval_infix_expression(operator: str, left: MObject, right: MObject):
    exp = (left, operator, right)
    match exp:
        case (MInteger(), "+", MInteger()):
            return cast(MInteger, left) + cast(MInteger, right)
        case (MInteger(), "-", MInteger()):
            return cast(MInteger, left) - cast(MInteger, right)
        case (MInteger(), "*", MInteger()):
            return cast(MInteger, left) * cast(MInteger, right)
        case (MInteger(), "/", MInteger()):
            return cast(MInteger, left) / cast(MInteger, right)
        case (MInteger(), "<", MInteger()):
            return MBoolean.from_bool(cast(MInteger, left) < cast(MInteger, right))
        case (MInteger(), ">", MInteger()):
            return MBoolean.from_bool(cast(MInteger, left) > cast(MInteger, right))
        case (MInteger(), "==", MInteger()):
            return MBoolean.from_bool(left == right)
        case (MInteger(), "!=", MInteger()):
            return MBoolean.from_bool(left != right)
        case (_, "==", _):
            return MBoolean.from_bool(left == right)
        case (_, "!=", _):
            return MBoolean.from_bool(left != right)
        case (_, _, _) if left.type_desc() != right.type_desc():
            return MError(
                f"type mismatch: {left.type_desc()} {operator} {right.type_desc()}"
            )
        case (MString(), "+", MString()):
            return left + right
        case (_, _, _):
            return MError(
                f"unknown operator: {left.type_desc()} {operator} {right.type_desc()}"
            )


def _eval_if_expression(if_expression: IfExpression, env):
    condition = _evaluate(nn(if_expression.condition), env)
    match condition:
        case MError():
            return condition
        case _:
            if _is_truthy(condition):
                return _evaluate(if_expression.consequence, env)
            if if_expression.alternative is not None:
                return _evaluate(if_expression.alternative, env)
            # else:
            return NULL


def _error(obj):
    return isinstance(obj, MError)


def _eval_expressions(arguments: list[Expression | None], env: Environment) -> list:
    args = []
    for argument in arguments:
        evaluated = _evaluate(argument, env)
        if _error(evaluated):
            return [evaluated]

        args.append(evaluated)
    return args


def _extend_function_env(function, args):
    env = Environment({}, function.env)
    for i, identifier in enumerate(function.parameters):
        env[identifier.value] = args[i]
    return env


def _unwrap_return_value(evaluated):
    match evaluated:
        case MReturnValue(value):
            return value
        case _:
            return evaluated


def _apply_function(function, args):
    match function:
        case MFunction():
            extend_env = _extend_function_env(function, args)
            evaluated = _evaluate(function.body, extend_env)
            return _unwrap_return_value(evaluated)
        case MBuiltinFunction():
            result = function.fn(args)
            if result is None:
                return NULL
            # else:
            return result
        case _:
            return MError(f"not a function: {function.type_desc()}")


def _eval_identifier(identifier: str, env: Environment):
    value = env[identifier]
    if value is not None:
        return value
    builtin = BUILTINS.get(identifier, None)
    return MError(f"identifier not found: {identifier}") if builtin is None else builtin


def _eval_hash_index_expression(pairs, index):
    match index:
        case MValue():
            pair = pairs.get(index.hash_key(), None)
            if pair is None:
                return NULL
            # else:
            return pair.value
        case _:
            return MError(f"unusable as a hash key: {index.type_desc()}")


def _eval_array_index_expression(elements, index):
    return NULL if index < 0 or index > (len(elements) - 1) else elements[index]


def _eval_index_expression(left, index):
    exp = (left, index)
    match exp:
        case (MArray(elements), MInteger(value)):
            return _eval_array_index_expression(elements, value)
        case (MHash(pairs), _):
            return _eval_hash_index_expression(pairs, index)
        case (_, _):
            return MError(f"index operator not supported: {left.type_desc()}")


def _eval_hash_literal(hash_pairs, env):
    pairs = {}
    for key_node, value_node in hash_pairs.items():
        key = _evaluate(key_node, env)
        if _error(key):
            return key
        match key:
            case MValue():
                value = _evaluate(value_node, env)
                if _error(value):
                    return value

                pairs[key.hash_key()] = HashPair(key, value)
            case _:
                return MError(f"unusable as hash key: {key.type_desc()}")
    return MHash(pairs)


def evaluate(program: Program, env: Environment):
    result = None
    for statement in program.statements:
        result = _evaluate(statement, env)
        match result:
            case MReturnValue(value):
                return value
            case MError():
                return result

    return result


def _evaluate(node: Statement, env: Environment):
    match node:
        case Identifier(value):
            return _eval_identifier(value, env)
        case IntegerLiteral(value):
            return MInteger(value)
        case InfixExpression(left, operator, right):
            return _if_not_error(
                _evaluate(nn(left), env),
                lambda l: _if_not_error(
                    _evaluate(nn(right), env),
                    lambda r: _eval_infix_expression(operator, l, r),
                ),
            )
        case BlockStatement():
            return _eval_block_statement(node, env)
        case ExpressionStatement(expression):
            return _evaluate(nn(expression), env)
        case IfExpression():
            return _eval_if_expression(node, env)
        case CallExpression(function, arguments):
            fn = _evaluate(nn(function), env)
            match fn:
                case MError():
                    return fn
                case _:
                    args = _eval_expressions(arguments, env)
                    if len(args) == 1 and _error(args[0]):
                        return args[0]

                    return _apply_function(fn, args)
        case ReturnStatement(value):
            return _if_not_error(_evaluate(nn(value), env), MReturnValue)
        case PrefixExpression(operator, right):
            return _if_not_error(
                _evaluate(nn(right), env), lambda r: _eval_prefix_expression(operator, r)
            )
        case BooleanLiteral(value):
            return MBoolean.from_bool(value)
        case LetStatement(name, value):
            let = _evaluate(nn(value), env)
            match let:
                case MError():
                    return let
                case _:
                    env[name.value] = let
                    return let
        case FunctionLiteral(parameters, body):
            return MFunction(parameters, body, env)
        case StringLiteral(value):
            return MString(value)
        case IndexExpression(left, index):
            left_evaluated = _evaluate(nn(left), env)
            if _error(left_evaluated):
                return left_evaluated

            index_evaluated = _evaluate(nn(index), env)
            if _error(index_evaluated):
                return index_evaluated

            return _eval_index_expression(left_evaluated, index_evaluated)
        case HashLiteral(pairs):
            return _eval_hash_literal(pairs, env)
        case ArrayLiteral(elements):
            elems = _eval_expressions(elements, env)
            if len(elems) == 1 and _error(elems[0]):
                return elems[0]
            # else
            return MArray(elems)
        case _:
            print(f"{node} => {type(node)}")
            return None


def _if_not_error(obj, body):
    match obj:
        case MError():
            return obj
        case _:
            return body(obj)


def _is_truthy(obj) -> bool:
    match obj:
        case MBoolean(value):
            return value
        case MNull():
            return False
        case _:
            return True
