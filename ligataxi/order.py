from datetime import datetime

from multipledispatch import dispatch

from .driver import Driver
from .route import Route
from .state import State
from .properties import Property, Reference
from .types import (
    Address,
    CarExtra,
    CarType,
    Location,
    DateTime,
    DriverExtra,
    Object,
    Sequence,
)


class Order(Object):
    id = Property(int, nullable=True)
    company_id = Property(int, nullable=True)
    state = Property(State, nullable=True, parent='order')
    price = Property(float, default=0.0)
    discount_price = Property(float, default=0.0)
    discount_percent = Property(float, default=0.0)
    distance = Property(int, default=0)
    create_time = Property(DateTime, nullable=True)
    done_time = Property(DateTime, nullable=True)
    pickup_time = Property(DateTime)
    car_type = Property(Reference(CarType, 'client.company.car_types'))
    car_extras = Property(Sequence(Reference(
        CarExtra, 'client.company.car_extras')))
    driver_extras = Property(Sequence(Reference(
        DriverExtra, 'client.company.driver_extras')))
    comment = Property(str, blank=True, nullable=True)
    pickup_address = Property(Address)
    destinations = Property(Sequence(Address))

    @dispatch()
    def __init__(self, client=None, **kwargs):
        self.client = client
        super(Order, self).__init__(**kwargs)

    @dispatch(dict)
    def __init__(self, d, client=None):
        self.client = client
        super(Order, self).__init__(d)

    @dispatch((Address, dict), datetime, (CarType, int))
    def __init__(self, pickup_address, pickup_time, car_type,
                 car_extras=None, driver_extras=None, destinations=None,
                 comment=None, client=None):
        self.client = client
        super(Order, self).__init__(pickup_address=pickup_address,
                                    pickup_time=pickup_time,
                                    car_type=car_type, car_extras=car_extras,
                                    driver_extras=driver_extras,
                                    destinations=destinations, comment=comment)

    @dispatch('Order')
    def __init__(self, d):
        self.client = d.client
        super(Order, self).__init__(d.dump())

    def get(self, *args):
        return self.client.get('order', self.id, *args)

    def post(self, *args, **kwargs):
        return self.client.post('order', self.id, *args, json=kwargs)

    def driver(self):
        return Driver(self.get('driver'), order=self)

    def driver_location(self):
        if State.ACCEPTED <= self.state <= State.IN_PROGRESS:
            return Location(self.get('driver', 'location'))

    def evaluate(self, rating, comment=None):
        if not 1.0 <= rating <= 5.0:
            raise ValueError('invalid rating value: %f' % rating)
        self.post('evaluate', rating=rating, comment=comment)

    def route(self):
        if self.distance > 0:
            route = self.get('route')
            return Route(route)

    def __call__(self):
        order = self.get()
        super(Order, self).update(order)

    def __repr__(self):
        return (
            '{c.__name__}(id={o.id}, company_id={o.company_id}, '
            'state={o.state!r}, price={o.price}, '
            'discount_price={o.discount_price}, '
            'discount_percent={o.discount_percent}, '
            'distance={o.distance}, create_time={o.create_time!r}, '
            'done_time={o.done_time!r}, pickup_time={o.pickup_time!r}, '
            'car_type={o.car_type!r}, car_extras={o.car_extras!r}, '
            'driver_extras={o.driver_extras!r}, comment={o.comment!r}, '
            'pickup_address={o.pickup_address!r}, '
            'destinations={o.destinations!r})'.format(c=type(self), o=self)
        )
