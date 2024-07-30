from typing import Generic, TypeVar

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


def test_generic_type_map():
    m1 = GenericTypeMap(IntStr)

    assert m1[X] is int
    assert m1[Y] is str

    m2 = GenericTypeMap(IntFloat)

    assert m2[X] is int
    assert m2[Y] is float

    m3 = GenericTypeMap(IntY)

    assert m3[X] is int
    assert m3[Y] is Y

    m4 = GenericTypeMap(IntStrFloat)

    assert m4[X] is int
    assert m4[Y] is str
    assert m4[Z] is float

    m5 = GenericTypeMap(IntByteFloat)

    assert m5[X] is int
    assert m5[Y] is bytes
    assert m5[Z] is float

    m6 = GenericTypeMap(IntYFloat)

    assert m6[X] is int
    assert m6[Y] is Y
    assert m6[Z] is float

    m7 = GenericTypeMap(IntStrBytes)

    assert m7[X] is int
    assert m7[Y] is str
    assert m7[Z] is bytes

    m8 = GenericTypeMap(XYBytes)

    assert m8[X] is X
    assert m8[Y] is Y
    assert m8[Z] is bytes

    m9 = GenericTypeMap(XyStrInt)

    assert m9[X] is str
    assert m9[Y] is int

    m10 = GenericTypeMap(YxBytesFloat)

    assert m10["X"] is float
    assert m10["Y"] is bytes
