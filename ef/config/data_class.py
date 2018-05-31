# https://codereview.stackexchange.com/questions/131761/lombokython-automatic-eq-hash-repr
# https://github.com/alexprengere/reprmixin
class DataClass:
    repr_arg_separator = ', '

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return repr(self) == repr(other)
        return NotImplemented

    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))

    def __repr__(self):
        return '{name}({values})'.format(
            name=type(self).__name__,
            values=self.repr_arg_separator.join(map(lambda pair: "{}={!r}".format(*pair), vars(self).items())))
