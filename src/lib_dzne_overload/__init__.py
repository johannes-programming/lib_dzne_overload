import inspect as _ins


class _Empty:
    pass


class Signature:
    def __eq__(self, other):
        if type(other) is not Signature:
            raise TypeError
        return self.keywords == other.keywords
    def __ne__(self, other):
        return not self.__eq__(other)
    def __init__(self, value):
        sig = _ins.signature(value)
        params = sig.parameters
        kinds = (_ins.Parameter.KEYWORD_ONLY, _ins.Parameter.POSITIONAL_OR_KEYWORD)
        self._keywords = list()
        for n, p in params.items():
            if p.kind not in kinds:
                raise ValueError(f"The parameter {n} of the callable {value.__name__} is of the illegal kind {p.kind}. ")
            self._keywords.append(n)
    @property
    def keywords(self):
        return frozenset(self._keywords)

class Overload:
    def __len__(self):
        return len(self._callables)
    def __iter__(self):
        return iter(self.callables)
    def __init__(self):
        self._callables = dict()
    def __call__(self, **kwargs):
        keywords = frozenset(kwargs.keys())
        return self[keywords](**kwargs)
    def __getitem__(self, key):
        keywords = self._getkeywords(key)
        if keywords not in self._callables.keys():
            raise KeyError(f"No fucntion with the keywords {keywords} has been appended to this overload. ")
        return self._callables[keywords]            
    def __setitem__(self, key, value):
        if not callable(value):
            raise ValueError("One cannot add an uncallable object to an overload! ")
        keywords = self._getkeywords(key)
        self._callables[keywords] = value
    def __delitem__(self, key):
        keywords = self._getkeywords(key)
        del self._callables[keywords]
    @classmethod
    def _getkeywords(cls, key):
        if type(key) is str:
            return frozenset([key])
        elif type(key) is tuple:
            return frozenset(key)
        elif type(key) is frozenset:
            return key
        raise TypeError

    @property
    def callables(self):
        return dict(self._callables)
    @callables.setter
    def callables(self, value):
        self._callables = dict(callables)

    def append(self, value, /):
        sig = Signature(value)
        if sig.keywords in self._callables.keys():
            raise KeyError(f"A callable with the keywords {sig.keywords} already exists within this overload. ")
        self._callables[sig.keywords] = value
        return value
    def extend(self, *values):
        for value in values:
            self.append(value)
    def pop(self, *keywords, default=_Empty):
        keywords = self._getkeywords(keywords)
        if default is _Empty:
            return self._callables.pop(keywords)
        else:
            return self._callables.pop(keywords, default)
    def to_dict(self):
        return self.callables
    def get(self, *keywords, default=None):
        keywords = self._getkeywords(keywords)
        try:
            return self._callables[keywords]
        except KeyError:
            return default
    def keys(self):
        return self.callables.keys()
    def values(self):
        return self.callables.values()
    def items(self):
        return self.callables.items()

