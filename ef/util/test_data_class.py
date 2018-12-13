import numpy as np

from ef.util.data_class import DataClass


class TestDataClass:
    class AB(DataClass):
        c = 10

        def __init__(self, a, b):
            self.a = a
            self.b = b

        @property
        def p(self):
            return self.a + self.b

        @classmethod
        def cm(cls):
            return cls(10, 20)

        @staticmethod
        def sm():
            return "foo"

    class AB2(AB):
        pass

    class ABx(AB):
        def __init__(self, a, b):
            super().__init__(a, b)
            self._x = a + b

    def test_dict(self):
        AB = self.AB
        ab = AB(1, 2)
        assert ab.dict == {'a': 1, 'b': 2}
        assert AB(ab, []).dict == {'a': ab, 'b': []}
        assert AB(**ab.dict) == ab
        assert self.ABx(1, 2).dict == {'a': 1, 'b': 2, '_x': 3}

    def test_eq(self):
        AB = self.AB
        ab = AB(1, 2)
        assert ab == ab
        assert ab == AB(1, 2)
        assert ab != AB(2, 2)
        assert ab == AB(1., 2)
        assert ab != (1, 2)
        assert ab != self.AB2(1, 2)
        assert ab != self.ABx(1, 2)
        ab.x = 10
        assert ab != AB(1, 2)
        assert AB([1, 2, 3], np.array([[4, 5, 6], [7, 8, 9]])) == \
               AB([1, 2, 3], np.array([[4, 5, 6], [7, 8, 9]]))
        assert AB([1, 2, 3], np.array([[4, 5, 6], [7, 8, 9]])) != \
               AB([1, 2, 3], np.array([[4, 5, 7], [7, 8, 9]]))
        assert AB([1, 2, 3], np.array([[4, 5, 6], [7, 8, 9]])) == \
               AB([1, 2, 3], np.array([[4, 5, 6.], [7, 8, 9]]))
        assert AB(AB(1, 2), 5) == AB(AB(1, 2), 5)
        assert AB(AB(1, 3), 5) != AB(AB(1, 2), 5)

    def test_nan(self):
        assert self.AB([1, 2, 3], np.array([[4, 5, np.NaN], [7, 8, 9]])) != \
               self.AB([1, 2, 3], np.array([[4, 5, np.NaN], [7, 8, 9]]))

    def test_str(self):
        assert str(self.AB(1, 2)) == "### AB:\na = 1\nb = 2"

    def test_repr(self):
        assert repr(self.AB(1, 2)) == "AB(a=1, b=2)"
