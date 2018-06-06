# https://codereview.stackexchange.com/questions/131761/lombokython-automatic-eq-hash-repr
# https://github.com/alexprengere/reprmixin
class DataClass:
    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return repr(self) == repr(other)
        return NotImplemented

    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))

    def __repr__(self):
        return '{name}({values})'.format(
            name=type(self).__name__,
            values=', '.join(map(lambda pair: "{}={!r}".format(*pair), vars(self).items())))
