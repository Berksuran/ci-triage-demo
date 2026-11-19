from demo.calc import add, total


def test_add():
    assert add(2, 2) == 4


def test_total():
    assert total(2, 2) == 4
