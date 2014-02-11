"""JSON-rendering helpers.

This module is not dependent on anything else inside Flask-arrest and may be
factored out into its own library at some point.

It provides mixins for the stdlib :class:`json.JSONEncoder` class, adding
serialization methods for other object types, such as
:class:`~datetime.datetime` objects or iterables.

All these are ready to use by using :data:`~flask_arrest.json.json_enc`.
"""

from __future__ import absolute_import

import datetime
import json

import times


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


class JSONToDictMixin(object):
    """A mixin for JSONEncoders, encoding any object with a to_dict() method
    by calling that method and encoding the return value."""
    def default(self, o):
        if hasattr(o, 'to_dict'):
            return o.to_dict()
        return super(JSONToDictMixin, self).default(o)


class ExtendedJSONEncoder(JSONDateTimeMixin,
                          JSONIterableMixin,
                          JSONToDictMixin,
                          json.JSONEncoder, object):
    pass


json_enc = ExtendedJSONEncoder()


# FIXME: this needs to be able to at least parse timestamps in the future
json_dec = json.JSONDecoder()
