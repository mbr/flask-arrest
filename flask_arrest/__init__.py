#!/usr/bin/env python

from functools import wraps

from flask import Blueprint, request, current_app, Response, make_response, \
    abort
from werkzeug.exceptions import HTTPException

from .encoding import json_enc, json_dec

__version__ = '0.3.dev2'


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
                rv = f(*fargs, **fkwargs)

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

        self.http_errorhandlers(self.__serializing_errorhandler)

    def http_errorhandlers(self, f):
        # there's an issue and a pull request for this at
        # https://github.com/mitsuhiko/flask/pull/952
        # for now, this is a workaround

        for i in range(0, 600):
            if i != 500:
                # AssertionError: It is currently not possible to register a
                # 500 internal server error on a per-blueprint level.
                self.errorhandler(i)(f)

        return f

    def __serializing_errorhandler(self, error):
        return serialize_response(error)


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
