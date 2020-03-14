import html
import json
import re

_tag_pattern = re.compile('<.+?>')


class LigaTaxiException(Exception):
    pass


class LigaTaxiApiError(LigaTaxiException):
    def __init__(self, response):
        try:
            message = response.json()['error_message']
        except (KeyError, json.JSONDecodeError):
            text = _tag_pattern.sub('', response.text)
            for line in reversed(text.splitlines()):
                msg = html.unescape(line.strip())
                if msg:
                    break
            else:
                msg = ''
            message = '{0}, {1}'.format(response.status_code, msg)
        super(LigaTaxiApiError, self).__init__(message)
