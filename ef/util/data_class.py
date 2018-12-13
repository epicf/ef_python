import numpy as np


class DataClass:
    """ Mixin class to implement default methods for hierarchies of simple objects containing ndarrays. """
    @property
    def dict(self):
        """
        Try overriding this first to customize a child class.

        :return: A dict representation of object attributes that can be used to construct it.
        """
        return vars(self)

    def __eq__(self, other):
        if self is other:
            return True
        if type(self) is not type(other):
            return NotImplemented
        if self.dict.keys() != other.dict.keys():
            return False
        for k, v in self.dict.items():
            w = other.dict[k]
            if isinstance(v, np.ndarray) or isinstance(w, np.ndarray):
                # Warning: NaN != NaN, may cause problems if array has NaNs
                if np.any(v != w):
                    return False
            else:
                if v != w:
                    return False
        return True

    def __hash__(self):
        return hash(tuple(sorted(self.dict.items())))

    def __repr__(self):
        cls = self.__class__.__name__
        args = ', '.join(f"{k}={v!r}" for k, v in self.dict.items())
        return f"{cls}({args})"

    def __str__(self):
        cls = self.__class__.__name__
        args = '\n'.join(f"{k} = {v}" for k, v in self.dict.items())
        return f"### {cls}:\n{args}"
