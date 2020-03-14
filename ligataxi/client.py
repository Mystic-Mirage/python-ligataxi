import json

from multipledispatch import dispatch

from .order import Order
from .profile import Profile
from .properties import Property
from .state import State
from .types import Object, Sequence


class Client(Object):
    phone = Property(str)
    uuid = Property(str, nullable=True)

    def __init__(self, phone, uuid=None, company=None):
        self.company = company
        super(Client, self).__init__(phone=phone, uuid=uuid)

    def get(self, *args, **kwargs):
        return self.company.get(*args, uuid=self.uuid, **kwargs)

    def post(self, *args, **kwargs):
        return self.company.post(*args, uuid=self.uuid, **kwargs)

    @dispatch()
    def auth(self):
        self.get('auth', phone=self.phone)

    @dispatch(str)
    def auth(self, code):
        res = self.post('auth', phone=self.phone, code=code)
        self.uuid = res['uuid']
        return self.uuid

    def calculate(self, *args, **kwargs):
        return self.company.calculate(*args, uuid=self.uuid, **kwargs)

    def order(self, state=State.ALL, limit=10, offset=0):
        return Sequence(Order)(
            self.get('order', state=state, limit=limit, offset=offset),
            client=self,
        )

    def profile(self):
        return Profile(self.get('profile'))

    def save(self, path):
        with open(path, 'w') as w:
            data = {'phone': self.phone, 'uuid': self.uuid}
            json.dump(data, w)

    def __repr__(self):
        return '{c.__name__}(phone={o.phone!r}, uuid={o.uuid!r})'.format(
            c=type(self), o=self,
        )
