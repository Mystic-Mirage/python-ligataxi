from .types import Object, Property


class Driver(Object):
    driver_name = Property(str)
    phone = Property(str)
    car_model = Property(str)
    car_color = Property(str)
    car_number = Property(str)

    def __init__(self, d, order=None):
        self.order = order
        super(Driver, self).__init__(d)

    def location(self):
        return self.order.driver_location()

    def __repr__(self):
        return (
            '{c.__name__}(driver_name={o.driver_name!r}, phone={o.phone!r}, '
            'car_model={o.car_model!r}, car_color={o.car_color!r}, '
            'car_number={o.car_number!r})'.format(c=type(self), o=self)
        )
