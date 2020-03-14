from multipledispatch import dispatch


class State(int):
    PROCESSING = 1
    ACCEPTED = 2
    ARRIVING = 3
    IN_PROGRESS = 4
    COMPLETED = 5
    CANCELED = 6
    NO_DRIVERS_AVAILABLE = 7
    RESERVED = 8
    ALL = 12345678
    _states = {}

    @dispatch(type, object)
    def __new__(cls, x, order=None):
        x = int(x)
        if x < 1:
            raise ValueError('positive non-zero integer required')
        state = cls._states.get(x)

        name = None
        if state is not None:
            if order is None:
                return state
            name = state.name

        state = super(State, cls).__new__(cls, x)
        state.name = name
        state.order = order

        return state

    @dispatch(type, 'State')
    def __new__(cls, x, order=None):
        return cls.__new__(cls, int(x), order=order or x.order)

    @dispatch(type, (list, tuple, str))
    def __new__(cls, x, order=None):
        x = int(''.join(sorted(set(map(str, x)))))
        return cls.__new__(cls, x, order=order)

    def __call__(self):
        if self.order:
            self.order.state = self.order.get('state')['state']
            return self.order.state
        raise TypeError("'%s' object is not callable" % type(self).__name__)

    def __contains__(self, x):
        return str(x) in str(self)

    def __or__(self, other):
        if not other:
            return State(self)
        order = self.order or getattr(other, 'order', None)
        return State(str(self) + str(other), order=order)

    __ror__ = __or__

    def __repr__(self):
        if self not in self._states and self > 9:
            return ' | '.join(repr(State(s)) for s in str(self))

        suffix = '({o!s})' if self.name is None else '.{o.name}'
        return ('{c.__name__}' + suffix).format(c=type(self), o=self)

    @classmethod
    def init(cls):
        for attr in dir(cls):
            value = getattr(cls, attr)
            if attr.isupper() and isinstance(value, int):
                state = cls(value)
                state.name = attr
                setattr(cls, attr, state)
                cls._states[value] = state


State.init()
