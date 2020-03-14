from datetime import datetime

from multipledispatch import dispatch

from .properties import Property
from .state import State

_datetime_format = '%Y-%m-%dT%H:%M:%S'


class Object(object):
    @dispatch()
    def __init__(self, **kwargs):
        self._dict = {}
        self.update(kwargs)

    @dispatch(dict)
    def __init__(self, d):
        self._dict = {}
        self.update(d)

    @dispatch(object)
    def __init__(self, d):
        self._dict = {}
        self.update(d.dump())

    def __getitem__(self, key):
        return self._dict[key]

    def __setitem__(self, key, value):
        self._dict[key] = value

    @classmethod
    def _props(cls):
        return [p for p in dir(cls) if isinstance(getattr(cls, p), Property)]

    def dump(self, fields=None):
        d = {}

        fields = fields or []
        props = [p for p in self._props() if fields is None or p in fields]

        for key in props:
            val = getattr(self, key)

            if isinstance(val, Object):
                val = val.dump()
            elif isinstance(val, State):
                val = int(val)
            elif isinstance(val, list):
                val = [i.dump() if isinstance(i, Object) else i for i in val]
            elif isinstance(val, datetime):
                val = val.strftime(_datetime_format)

            d[key] = val

        return d

    def update(self, d):
        for key, value in d.items():
            setattr(self, key, value)


class Simple(Object):
    id = Property(int)
    name = Property(str, blank=True, nullable=True)

    def dump(self, fields=None):
        return self.id

    def __repr__(self):
        return '{c.__name__}(id={o.id}, name={o.name!r})'.format(c=type(self),
                                                                 o=self)

    def __str__(self):
        return self.name


class CancelReason(Simple):
    pass


class CarType(Simple):
    def __init__(self, d, company=None, order=None):
        self.company = company
        self.order = order
        super(CarType, self).__init__(d)


class CarExtra(Simple):
    pass


class Location(Object):
    lat = Property(float)
    lng = Property(float)

    def __init__(self, loc=None, **kwargs):
        if isinstance(loc, (list, tuple)):
            super(Location, self).__init__()
            self.lat, self.lng = loc
        else:
            super(Location, self).__init__(loc, **kwargs)

    def __repr__(self):
        return '{c.__name__}(lat={o.lat}, lng={o.lng})'.format(c=type(self),
                                                               o=self)


class Point(Location):
    pass


class Area(Object):
    ne = Property(Point)
    sw = Property(Point)

    def __init__(self, a):
        super(Area, self).__init__()
        self.ne, self.sw = a

    def dump(self, fields=None):
        return [self.ne.dump(), self.sw.dump()]

    def __repr__(self):
        return '{c.__name__}([{o.ne!r}, {o.sw!r}])'.format(c=type(self),
                                                           o=self)


class Address(Location):
    street = Property(str)
    building = Property(str)
    comment = Property(str, nullable=True)

    def location(self):
        return Location((self.lat, self.lng))

    def __repr__(self):
        return (
            '{c.__name__}(street={o.street!r}, building={o.building!r}, '
            'comment={o.comment!r}, lat={o.lat}, lng={o.lng})'.format(
                c=type(self), o=self,
            )
        )


class DriverExtra(Simple):
    pass


class DateTime(object):
    def __new__(cls, d):
        if isinstance(d, datetime):
            return d.replace(microsecond=0)
        return datetime.strptime(d, _datetime_format)


class Sequence(object):
    def __init__(self, t):
        self.type = t

    def __instancecheck__(self, instance):
        return isinstance(instance, self.type)

    def __call__(self, lst=None, **kwargs):
        if lst is None:
            return []
        return [self.type(i, **kwargs) for i in lst]

    def __repr__(self):
        return '{c.__name__}({o.type.__name__})'.format(c=type(self), o=self)

    __name__ = property(__repr__)
