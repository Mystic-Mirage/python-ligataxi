from .route import Route
from .types import Object, Property


class Estimate(Object):
    distance = Property(int)
    price = Property(float)
    driving_time = Property(int)
    discount_price = Property(float)
    discount_percent = Property(float)
    route = Property(Route)

    def __repr__(self):
        return (
            '{c.__name__}(distance={o.distance}, price={o.price}, '
            'driving_time={o.driving_time}, '
            'discount_price={o.discount_price}, '
            'discount_percent={o.discount_percent}, route={o.route!r})'.format(
                c=type(self), o=self,
            )
        )
