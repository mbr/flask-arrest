#!/usr/bin/env python

import datetime
from functools import wraps
import json

from flask import Blueprint, request, current_app, Response, make_response, \
    abort
import times
from werkzeug.exceptions import HTTPException

__version__ = '0.2.2.dev1'


# NOTE: This is code that probably belongs in submodules at some point.
# However, since the codebase is so small, we keep everything in here.


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


class ContentNegotiationMixin(object):
    """A blueprint mixin that supports content negotiation. Used in conjunction
    with the :func:`get_best_mimetype()` and :func:`serializer_response()`
    functions.

    A mimetype is a string describing a mime(Content-)type, serializers are
    callables that convert a single argument into a string representation.

    If no encoder mapping is supplied using ``response_mimetypes``, a single
    mapping is used, mapping ``application/json`` to an instance of
    ``RESTJSONEncoder``."""
    def add_response_type(self, mimetype, serializer='json'):
        if serializer == 'json':
            serializer = json_enc.encode
        if not hasattr(self, 'response_mimetypes'):
            self.response_mimetypes = {}
        self.response_mimetypes[mimetype] = serializer


def get_best_mimetype():
    """Returns the highest quality mimetype-string that client and server can
    agree on. Returns ``None``, if no suitable type is found."""
    # find out what the client accepts
    return request.accept_mimetypes.best_match(
        current_app.blueprints[request.blueprint].response_mimetypes.keys()
    )


def serialize_response(response_data, content_type=None):
    """Serializes a response using a specified serializer.

    If ``response_data`` is an instance of
    :class:`~werkzeug.exceptions.HTTPException`, the status code of the
    response will be set accordingly.

    :param response_data: Data to be serialized. Can be anything the serializer
                          can handle.
    :param content_type: The Content-type to serialize for. Must be registered
                         on the blueprint, will use :meth:`get_best_mimetype()`
                         if ``None``.
    :return: A :class:`~flask.Response` object."""
    content_type = content_type or get_best_mimetype()

    if not content_type:
        abort(406)

    rv = current_app.blueprints[request.blueprint]\
        .response_mimetypes[content_type](response_data)

    response = make_response(rv)

    if isinstance(response_data, HTTPException):
        response.status_code = response_data.code

    response.headers['Content-type'] = content_type
    return response


class RestMixin(ContentNegotiationMixin):
    """A REST Blueprint.

    Deriving from :class:`ContentNegotiatingBlueprint`, any route is decorated
    with an extra function causing all returns values to be run through
    :func:`serialize_response`, unless they are already an instance of
    :class:`flask.Response`.

    Any :class:`~werkzeug.exceptions.HTTPException` will be serialized as well,
    other exceptions will be passed through unchanged (triggering 500 errors
    or the debugger, depending on whether ``DEBUG`` is enabled)."""

    def route(self, *rargs, **rkwargs):
        def wrapper(f):
            @wraps(f)
            def _(*fargs, **fkwargs):
                try:
                    rv = f(*fargs, **fkwargs)
                except HTTPException as e:
                    rv = e

                if isinstance(rv, Response):
                    # keep unchanged if already instance of Response
                    return rv

                # return serialized response
                return serialize_response(rv)

            # wrapped in original route function
            return super(RestMixin, self).route(*rargs, **rkwargs)(_)

        return wrapper


def parse_request_data():
    if not request.headers.get('Content-type', None):
        if request.data:
            abort(415, 'No Content-type specified for request body.')

        # no content type
        request.parsed_data = None
        return

    content_type = request.headers['Content-type']
    blueprint = current_app.blueprints[request.blueprint]
    if not content_type in blueprint.request_mimetypes:
        abort(415, 'Request data must be of the following mimetypes: %s' %
                   ', '.join(sorted(blueprint.request_mimetypes.keys())))

    if not request.data:
        abort(400, 'Valid content-type given, but missing data.')

    # we've got a valid, supported mimetype, parse it
    try:
        request.parsed_data = blueprint.request_mimetypes[content_type](
            request.data
        )
    except Exception:
        abort(400, 'Error deserializing content.')


class DeserializingMixin(object):
    def add_request_type(self, mimetype, deserializer='json'):
        if deserializer == 'json':
            deserializer = json_dec.decode
        if not hasattr(self, 'request_mimetypes'):
            self.request_mimetypes = {}
        self.request_mimetypes[mimetype] = deserializer


class RestBlueprint(DeserializingMixin, RestMixin, Blueprint):
    def __init__(self, *args, **kwargs):
        super(RestBlueprint, self).__init__(*args, **kwargs)
        self.before_request(parse_request_data)
        self.response_mimetypes = {}


# restricting decorators
def accepts(*args):
    def wrapper(f):
        @wraps(f)
        def _(*args, **kwargs):
            if not request.mimetype in args:
                abort(415, 'Request must be one of the following mimetypes: %s'
                           % ','.join(args))
            return f(*args, **kwargs)
    return wrapper


def produces(*args):
    def wrapper(f):
        @wraps(f)
        def _(*args, **kwargs):
            for mimetype in args:
                if mimetype in request.accept_mimetypes:
                    return f(*args, **kwargs)
            abort(406)
    return wrapper
