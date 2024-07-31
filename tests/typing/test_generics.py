from typing import Generic, TypeVar

import pytest

from theutilitybelt.typing.generics import GenericTypeMap

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
