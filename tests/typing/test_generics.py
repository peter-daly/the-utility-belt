from typing import Generic, Protocol, TypeVar

import pytest

from theutilitybelt.typing.generics import (
    GenericTypeMap,
    get_generic_type_args,
    try_to_map_generic_args_to_open_type,
)

X = TypeVar("X")
Y = TypeVar("Y")
Z = TypeVar("Z")


class TestXY(Generic[X, Y]):
    pass


class IntStr(TestXY[int, str]):
    pass


class IntY(TestXY[int, Y], Generic[Y]):
    pass


class IntFloat(IntY[float]):
    pass


class TestXYZ(Generic[X, Y, Z]):
    pass


class IntStrFloat(TestXYZ[int, str, float]):
    pass


class IntYFloat(TestXYZ[int, Y, float], Generic[Y]):
    pass


class IntByteFloat(IntYFloat[bytes]):
    pass


class XYBytes(TestXYZ[X, Y, bytes], Generic[X, Y]):
    pass


class IntYBytes(XYBytes[int, Y], Generic[Y]):
    pass


class IntStrBytes(IntYBytes[str]):
    pass


class XGeneric(Generic[X]):
    pass


class YGeneric(Generic[Y]):
    pass


class XyStrInt(XGeneric[str], YGeneric[int]):
    pass


class YxBytesFloat(YGeneric[bytes], XGeneric[float]):
    pass


class Parent(Generic[X]):
    pass


class Child(Parent[Y], Generic[Y]):
    pass


class GrandChild(Child[int]):
    pass


TOperation = TypeVar("TOperation")
TOperationResult = TypeVar("TOperationResult")


class Command:
    pass


TCommand = TypeVar("TCommand", bound=Command)


class Query:
    pass


class QueryResult:
    pass


TQuery = TypeVar("TQuery", bound=Query)
TQueryResult = TypeVar("TQueryResult", bound=QueryResult)


class ACommand(Command):
    pass


class BQuery(Query):
    pass


class BQueryResult(QueryResult):
    pass


class OperationHandler(Protocol[TOperation, TOperationResult]):
    pass


class CommandHandler(OperationHandler[TCommand, None], Protocol[TCommand]):
    pass


class QueryHandler(
    OperationHandler[TQuery, TQueryResult], Protocol[TQuery, TQueryResult]
):
    pass


class AHandler(CommandHandler[ACommand]):
    pass


class BHandler(QueryHandler[BQuery, BQueryResult]):
    pass


@pytest.mark.parametrize(
    "test_type, x, y",
    [
        (TestXY, X, Y),
        (IntStr, int, str),
        (IntFloat, int, float),
        (IntY, int, Y),
        (XyStrInt, str, int),
        (YxBytesFloat, float, bytes),
    ],
)
def test_two_generic_type_args(test_type: type, x: type, y: type):
    mapping = GenericTypeMap(test_type)
    assert mapping[X] is x
    assert mapping[Y] is y


@pytest.mark.parametrize(
    "test_type, x, y, z",
    [
        (IntStrFloat, int, str, float),
        (IntByteFloat, int, bytes, float),
        (IntYFloat, int, Y, float),
        (IntStrBytes, int, str, bytes),
        (XYBytes, X, Y, bytes),
    ],
)
def test_three_generic_type_args(test_type: type, x: type, y: type, z: type):
    mapping = GenericTypeMap(test_type)
    assert mapping[X] is x
    assert mapping[Y] is y
    assert mapping[Z] is z


@pytest.mark.parametrize(
    "test_type, expected",
    [
        (TestXY, True),
        (IntStr, False),
        (IntY, True),
        (IntFloat, False),
        (TestXYZ, True),
        (IntStrFloat, False),
        (IntYFloat, True),
        (IntByteFloat, False),
        (XYBytes, True),
        (IntYBytes, True),
        (IntYBytes, True),
        (IntStrBytes, False),
        (XGeneric, True),
        (YGeneric, True),
        (XyStrInt, False),
        (int, False),
    ],
)
def test_is_generic_mapping_open(test_type: type, expected: bool):
    mapping = GenericTypeMap(test_type)
    assert mapping.is_generic_mapping_open() is expected


def test_recursive_linking_in_mappings():
    a_map = GenericTypeMap(AHandler)
    b_map = GenericTypeMap(BHandler)

    assert a_map[TOperation] is ACommand
    assert a_map[TOperationResult] is type(None)
    assert a_map[TCommand] is ACommand

    assert b_map[TOperation] is BQuery
    assert b_map[TOperationResult] is BQueryResult
    assert b_map[TQuery] is BQuery
    assert b_map[TQueryResult] is BQueryResult


def test_is_singleton_per_type():
    mapping1 = GenericTypeMap(IntY)
    mapping2 = GenericTypeMap(IntY)
    mapping3 = GenericTypeMap(IntStr)

    assert mapping1 is mapping2

    assert mapping1 is not mapping3


@pytest.mark.parametrize(
    "open_type, closed_type, result_type",
    [
        (OperationHandler, AHandler, OperationHandler[ACommand, None]),
        (OperationHandler, BHandler, OperationHandler[BQuery, BQueryResult]),
        (CommandHandler, AHandler, CommandHandler[ACommand]),
        (QueryHandler, BHandler, QueryHandler[BQuery, BQueryResult]),
    ],
)
def test_try_to_complete_generic(open_type, closed_type, result_type):
    assert try_to_map_generic_args_to_open_type(open_type, closed_type) == result_type


@pytest.mark.parametrize(
    "test_type, expected",
    [
        (TestXY, (X, Y)),
        (CommandHandler, (TCommand,)),
        (CommandHandler[TCommand], (TCommand,)),  # type: ignore
        (AHandler, (TCommand,)),
        (int, tuple()),
    ],
)
def test_get_generic_type_args(test_type, expected):
    result = get_generic_type_args(test_type)
    assert result == expected
