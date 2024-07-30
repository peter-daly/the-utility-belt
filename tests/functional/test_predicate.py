from theutilitybelt.functional.predicate import predicate


def test_name():
    def f():
        return True

    def g():
        return True

    p1 = predicate(f)
    p2 = predicate(g)

    assert p1.__name__ == "f"
    assert p2.__name__ == "g"


def test_logic_operations():
    def f():
        return True

    def g():
        return False

    pf = predicate(f)
    pg = predicate(g)

    pand = pf & pg
    por = pf | pg
    pxor = pf ^ pg
    pinv = ~pf

    assert pand() is False
    assert por() is True
    assert pxor() is True
    assert pinv() is False

    assert pand.__name__ == "f_and_g"
    assert por.__name__ == "f_or_g"
    assert pxor.__name__ == "f_xor_g"
    assert pinv.__name__ == "not_f"
