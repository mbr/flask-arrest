from __future__ import absolute_import

import datetime
import json

import times
from werkzeug.exceptions import HTTPException


class JSONDateTimeMixin(object):
    """A mixin for JSONEncoders, encoding :class:`datetime.datetime` and
    :class:`datetime.date` objects by converting them to UNIX timetuples."""
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return times.format(o, 'Zulu')
        if isinstance(o, datetime.date):
            return o.isoformat()
        return super(JSONDateTimeMixin, self).default(o)


class JSONIterableMixin(object):
    """A mixin for JSONEncoders, encoding any iterable type by converting it to
    a list.

    Especially useful for SQLAlchemy results that look a lot like regular lists
    or iterators, but will trip up the encoder."""
    def default(self, o):
        try:
            iterable = iter(o)
        except TypeError:
            pass
        else:
            return list(iterable)
        return super(JSONIterableMixin, self).default(o)


class JSONHTTPErrorMixin(object):
    """A mixin for JSONEncoders, encoding
    :class:`~werkzeug.exceptions.HTTPException` instances.

    The format is similiar to::

        {
          "error": {"description": "You need to login",
                    "code": 401}
        }
    """
    def default(self, o):
        if isinstance(o, HTTPException):
            return {
                'error': {
                    'description': o.description,
                    'code': o.code,
                }
            }
        super(JSONHTTPErrorMixin, self).default(o)


class RESTJSONEncoder(JSONDateTimeMixin,
                      JSONHTTPErrorMixin,
                      JSONIterableMixin,
                      json.JSONEncoder, object):
    pass


json_enc = RESTJSONEncoder()
json_dec = json.JSONDecoder()
