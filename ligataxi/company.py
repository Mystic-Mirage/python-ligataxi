import json
from datetime import datetime, timedelta

from multipledispatch import dispatch

from .client import Client
from .estimate import Estimate
from .order import Order
from .properties import Property
from .types import (
    Address,
    Area,
    CarExtra,
    CarType,
    Location,
    DriverExtra,
    Object,
    Point,
    Sequence,
)


class Company(Object):
    id = Property(int)
    name = Property(str)
    max_pickup_time = Property(int)
    default_pickup_time = Property(int)
    driver_contact_method = Property(int)
    city = Property(str)
    region = Property(str)
    map_center = Property(Point)
    areas = Property(Sequence(Area))
    car_types = Property(Sequence(CarType), parent='company')
    car_extras = Property(Sequence(CarExtra))
    driver_extras = Property(Sequence(DriverExtra))
    cash_payment_type_id = Property(int, nullable=True)
    credit_card_payment_type_id = Property(int, nullable=True)
    bonus_payment_type_id = Property(int, nullable=True)

    def __init__(self, d, api=None):
        self.api = api
        super(Company, self).__init__(d)

    def get(self, *args, **kwargs):
        return self.api.get('company', self.id, *args, **kwargs)

    def post(self, *args, **kwargs):
        return self.api.post('company', self.id, *args, **kwargs)

    def about(self):
        return self.get('about')['about']

    def auth(self, phone):
        self.get('auth', phone=phone)
        return Client(phone, company=self)

    def load_client(self, path):
        with open(path) as r:
            data = json.load(r)
        return Client(company=self, **data)

    @dispatch(Order)
    def calculate(self, order, pickup_time=None, return_route=False,
                  uuid=None):
        if not order.destinations:
            return

        new_order = Order(order)

        if pickup_time is None:
            now = datetime.now()
            pickup_now = now + timedelta(minutes=self.default_pickup_time)

            if order.pickup_time < pickup_now:
                new_order.pickup_time = pickup_now

        request = new_order.dump(fields=[
            'pickup_address', 'pickup_time', 'car_type',
            'car_extras', 'driver_extras', 'destinations',
        ])
        request['return_route'] = return_route

        return Estimate(self.post('calculate', json=request, uuid=uuid))

    @dispatch((Address, dict), datetime, (CarType, int), list)
    def calculate(self, pickup_address, pickup_time, car_type,
                  destinations, car_extras=None, driver_extras=None,
                  return_route=False, uuid=None):
        order = Order(pickup_address, pickup_time, car_type, car_extras,
                      driver_extras, destinations)
        return self.calculate(order, return_route=return_route, uuid=uuid)

    def drivers(self):
        return Sequence(Location)(self.get('drivers')['drivers'])

    def phones(self):
        return self.get('phones')

    def __repr__(self):
        return (
            '{c.__name__}(id={o.id}, name={o.name!r}, '
            'max_pickup_time={o.max_pickup_time}, '
            'default_pickup_time={o.default_pickup_time}, '
            'driver_contact_method={o.driver_contact_method}, '
            'city={o.city!r}, region={o.region!r}, '
            'map_center={o.map_center!r}, areas={o.areas!r}, '
            'car_types={o.car_types!r}, car_extras={o.car_extras!r}, '
            'driver_extras={o.driver_extras!r}, '
            'cash_payment_type_id={o.cash_payment_type_id}, '
            'credit_card_payment_type_id={o.credit_card_payment_type_id}, '
            'bonus_payment_type_id={o.bonus_payment_type_id})'.format(
                c=type(self), o=self,
            )
        )
