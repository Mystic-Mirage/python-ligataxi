import polyline
from multipledispatch import dispatch

from .types import Point, Sequence


class Route(object):
    @dispatch((list, tuple))
    def __init__(self, route):
        self.points = list(route)

    @dispatch(str)
    def __init__(self, route):
        self.points = Sequence(Point)(polyline.decode(route))

    def __repr__(self):
        return '{c.__name__}({o.points!r})'.format(c=type(self), o=self)
