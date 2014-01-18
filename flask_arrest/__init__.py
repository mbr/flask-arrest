#!/usr/bin/env python

from functools import wraps

from flask import Blueprint, request, current_app, make_response, abort
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

    def __init__(self, *args, **kwargs):
        super(ContentNegotiationMixin, self).__init__(*args, **kwargs)
        self.before_request(self.__check_incoming_content_type)

    def add_response_type(self, mimetype, serializer='json'):
        if serializer == 'json':
            serializer = json_enc.encode
        if not hasattr(self, 'response_mimetypes'):
            self.response_mimetypes = {}
        self.response_mimetypes[mimetype] = serializer

    def __check_incoming_content_type(self):
        if not request.content_type and (request.data or request.form):
            abort(415)  # client needs to send a content-type, if he sends
                        # content

        if not request.content_type and not (request.data or request.form):
            return  # no content, no problem

        accepted = self.get_accepted_mimetypes(request.endpoint)
        if not request.content_type in accepted:
            abort(415)


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
        return HTTPException(406)

    rv = current_app.blueprints[request.blueprint]\
        .response_mimetypes[content_type](response_data)

    response = make_response(rv)

    if isinstance(response_data, HTTPException):
        response.status_code = response_data.code

    response.headers['Content-type'] = content_type
    return response


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


class RestBlueprint(ContentNegotiationMixin, DeserializingMixin, Blueprint):
    """A REST Blueprint.

    Deriving from :class:`ContentNegotiatingBlueprint`, all HTTPExcptions
    thrown are handled by the :func:`~RestMixin.rest_http_exceptionhandler`
    exception handler. The default implementation renders the exceptions into a
    format suitable for the client, while passing on the code unchanged."""

    def __init__(self, *args, **kwargs):
        super(RestBlueprint, self).__init__(*args, **kwargs)
        self.before_request(parse_request_data)
        self.response_mimetypes = {}

        self.http_errorhandlers(self.__serializing_errorhandler)
        self.accepted_mimetypes = {
            None: set(['application/json']),  # defaults for most common use
                                              # cases
        }

    def set_accepted_mimetypes(self, mimes, endpoint=None):
        if endpoint is None and None in mimes:
            raise ValueError('Cannot use None-value on default.')
        self.accepted_mimetypes[endpoint] = set(mimes)

    def add_accepted_mimetype(self, mime, endpoint=None):
        if endpoint is None and mime is None:
            raise ValueError('Cannot add None-value to default.')
        self.accepted_mimetypes.setdefault(endpoint, set([None])).add(mime)

    def get_accepted_mimetypes(self, endpoint=None):
        mimetypes = set(self.accepted_mimetypes.get(endpoint, set([None])))
        if None in mimetypes:
            mimetypes.remove(None)

            # add default types
            mimetypes.update(self.accepted_mimetypes[None])
        return mimetypes

    def http_errorhandlers(self, f):
        # there's an issue and a pull request for this at
        # https://github.com/mitsuhiko/flask/pull/952
        # for now, this is a workaround
        # ideally, we would just myblueprint.errorhandler(HTTPException)(f)

        for i in range(0, 600):
            if i != 500:
                # AssertionError: It is currently not possible to register a
                # 500 internal server error on a per-blueprint level.
                self.errorhandler(i)(f)
        return f

    def __serializing_errorhandler(self, error):
        return serialize_response(error), getattr(error, 'code', 500)


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
