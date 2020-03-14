from .properties import Property
from .types import Object, Sequence


class Profile(Object):
    name = Property(str)
    email = Property(str)
    success_orders = Property(int)
    reject_orders = Property(int)
    discount_number = Property(str, nullable=True)
    discount_sum = Property(float)
    discount_percent = Property(float)
    bonus_balance = Property(float)
    phones = Property(Sequence(str))

    def __repr__(self):
        return (
            '{c.__name__}(name={o.name!r}, email={o.email!r}, '
            'success_orders={o.success_orders}, '
            'reject_orders={o.reject_orders}, '
            'discount_number={o.discount_number}, '
            'discount_sum={o.discount_sum}, '
            'discount_percent={o.discount_percent}, '
            'bonus_balance={o.bonus_balance}, '
            'phones={o.phones!r})'.format(c=type(self), o=self)
        )
