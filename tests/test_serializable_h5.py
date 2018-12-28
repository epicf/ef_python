import h5py
import numpy as np

from ef.util.serializable_h5 import SerializableH5


class A(SerializableH5):
    def __init__(self, a, b):
        self.a = a
        self.b = b


def test_serializable_h5(tmpdir):
    fname = tmpdir.join("test.h5")
    a = A(1, 2)
    with h5py.File(fname, "w") as h5:
        a.save_h5(h5)
    with h5py.File(fname, "r") as h5:
        assert A.load_h5(h5) == a
    a = A(np.arange(100), A(np.array(((1., 2.), (3., 4.))), list('hello')))
    with h5py.File(fname, "w") as h5:
        a.save_h5(h5)
    with h5py.File(fname, "r") as h5:
        b = A.load_h5(h5)
        assert b == a
