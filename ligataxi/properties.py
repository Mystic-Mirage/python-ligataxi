class Property(object):
    def __init__(self, t, blank=False, default=None, nullable=False,
                 parent=None):
        self.type = t
        self.blank = blank
        self.default = default
        self.nullable = nullable
        self.parent = parent or isinstance(t, Reference) and 'parent' or None

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        try:
            return instance[self]
        except KeyError:
            return self.default

    def __set__(self, instance, value):
        if value is None and self.nullable:
            if self.blank:
                value = self.type()
        elif not isinstance(value, self.type):
            if self.parent:
                kwargs = {self.parent: instance}
                value = self.type(value, **kwargs)
            else:
                value = self.type(value)
        instance[self] = value

    def __repr__(self):
        return '{c.__name__}({o.type.__name__})'.format(c=type(self), o=self)


class Reference(object):
    def __init__(self, t, ref):
        self.type = t
        self.ref = ref

    def __instancecheck__(self, instance):
        return isinstance(instance, self.type)

    def __call__(self, x, parent):
        if isinstance(x, self.type):
            return x

        value = parent
        for key in self.ref.split('.'):
            value = getattr(value, key, [])
        for item in value:
            if item.id == x:
                return item

        return self.type({'id': x, 'name': '?'})

    def __repr__(self):
        return '{c.__name__}({o.type.__name__}, {o.ref!r})'.format(
            c=type(self), o=self,
        )

    __name__ = property(__repr__)


