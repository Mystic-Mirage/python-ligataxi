import itertools
import json as _json

import requests
from requests import compat

from .company import Company
from .exceptions import LigaTaxiApiError
from .properties import Property
from .types import CancelReason, Object, Sequence


class ApiBase(Object):
    scheme = 'https'
    base_domain = 'ligataxi.com'
    domain_prefix = ''
    base_path = 'api/v1'
    path = None

    domain = Property(str)
    api_key = Property(str)

    def __init__(self, domain, api_key):
        super(ApiBase, self).__init__(domain=domain, api_key=api_key)
        netloc = '{prefix}{domain}.{base}'.format(prefix=self.domain_prefix,
                                                  domain=self.domain,
                                                  base=self.base_domain)
        components = (self.scheme, netloc, self.base_path, None, None, None)
        url = compat.urlunparse(components)
        url = '/'.join(filter(None, [url, self.path]))
        self._base_url = url

    @classmethod
    def load(cls, path):
        with open(path) as r:
            data = _json.load(r)
        return cls(**data)

    def save(self, path):
        with open(path, 'w') as w:
            _json.dump(self.dump(), w)

    def _headers(self, uuid):
        headers = {'api-key': self.api_key}
        if uuid:
            headers['uuid'] = uuid
        return headers

    def _url(self, *args):
        req_path = map(str, filter(None, args))
        url = '/'.join(itertools.chain([self._base_url], req_path, ['']))
        return url

    def get(self, *args, uuid=None, **kwargs):
        url = self._url(*args)
        headers = self._headers(uuid=uuid)

        response = requests.get(url, headers=headers, params=kwargs)

        if response.ok:
            return response.json() if response.content else None

        raise LigaTaxiApiError(response)

    def post(self, *args, json=None, uuid=None, **kwargs):
        url = self._url(*args)

        headers = self._headers(uuid=uuid)

        if json is None:
            response = requests.post(url, data=kwargs, headers=headers)
        else:
            response = requests.post(url, json=json, headers=headers)

        if response.ok:
            return response.json() if response.content else None

        raise LigaTaxiApiError(response)

    def __repr__(self):
        return '{c.__name__}(domain={o.domain}, api_key={o.api_key})'.format(
            c=type(self), o=self,
        )


class LigaTaxiApi(ApiBase):
    domain_prefix = 'api-'
    path = 'client'

    def cancel_reasons(self):
        return Sequence(CancelReason)(self.get('cancel_reasons'))

    def company(self):
        return Sequence(Company)(self.get('company'), api=self)


class LigaTaxiAppApi(ApiBase):
    path = 'client_app'

    def localities(self, company_id=None):
        return self.get('localities', company_id=company_id)

    def autocomplete(self, company_id=None, q=''):
        return self.get('autocomplete', company_id=company_id, q=q)
