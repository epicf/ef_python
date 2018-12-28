from ef.util.subclasses import get_all_subclasses


def test_all_subclasses():
    class A0:
        pass

    class B0:
        pass

    assert get_all_subclasses(A0) == set()

    class A1(A0):
        pass

    class B1(B0):
        pass

    class A2(A1):
        pass

    class M1(A0, B1):
        pass

    class M2(A2, B0):
        pass

    assert get_all_subclasses(A0) == {A1, A2, M1, M2}
    assert get_all_subclasses(B0) == {B1, M1, M2}
    assert get_all_subclasses(B1) == {M1}
