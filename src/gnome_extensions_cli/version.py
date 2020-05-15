from functools import total_ordering
from itertools import zip_longest


@total_ordering
class Version:
    def __init__(self, version: str):
        self.__version = str(version)

    @property
    def value(self):
        return self.__version.strip()

    def __str__(self):
        return self.value

    def __hash__(self):
        return hash(self.value)

    def __eq__(self, other):
        if isinstance(other, str):
            return self.__eq__(Version(other))
        if not isinstance(other, Version):
            return NotImplemented
        return version_comparator(self.value, other.value) == 0

    def __lt__(self, other):
        if isinstance(other, str):
            return self.__lt__(Version(other))
        return version_comparator(self.value, other.value) < 0


def version_comparator(a: str, b: str):
    # Check inputs
    assert isinstance(a, str)
    assert isinstance(b, str)

    def parse_str(version: str):
        def tryint(x):
            try:
                return int(x)
            except Exception:
                return x

        return tuple(map(tryint, version.strip().split(".")))

    # extract tuples
    a, b = parse_str(a), parse_str(b)

    # Check equality
    if a == b:
        return 0

    # Iterate over values
    for va, vb in zip_longest(a, b):
        # Detect shorter version
        if va is None:
            return -1
        if vb is None:
            return 1
        # If different type, use str comparison
        if type(va) != type(vb):
            va, vb = str(va), str(vb)
        if va < vb:
            return -1
        if va > vb:
            return 1

    # Tuple are equal
    return 0
