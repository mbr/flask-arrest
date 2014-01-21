#!/usr/bin/env python

from flask import Blueprint, request, abort, make_response
from flask.helpers import locked_cached_property
from jinja2 import PackageLoader, ChoiceLoader, Environment
from werkzeug.exceptions import NotAcceptable

from .helpers import get_best_mimetype, current_blueprint, MIMEMap
from . import renderers

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

        self.incoming = MIMEMap()
        self.incoming.add_mimetype('application/json')

        self.outgoing = MIMEMap()
        self.outgoing.add_mimetype('application/json')

    def __check_incoming_content_type(self):
        if not request.content_type and (request.data or request.form):
            abort(415)  # client needs to send a content-type, if he sends
                        # content

        if not request.content_type and not (request.data or request.form):
            return  # no content, no problem

        accepted = self.incoming.get_mimetypes(request.endpoint)
        if not request.content_type in accepted:
            abort(415)


def serialize_response(response_data, content_type=None, renderer=None):
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
        # no accepted content-type. send flasks default 406, instead of raising
        return NotAcceptable()

    if not renderer:
        renderer = current_blueprint.content_renderer
    return renderer.render_response(response_data, content_type)


class AbsoluteJinjaEnvMixin(object):
    @locked_cached_property
    def _absolute_jinja_loader(self):
        # we override this so we can add our own template path as well as the
        # the one of any deriving blueprint
        #
        # templates are stored in flask_arrest/templates
        exc_loader = PackageLoader(__name__.rsplit('.', 1)[0])
        if not self.jinja_loader:
            return exc_loader

        return ChoiceLoader([self.jinja_loader, exc_loader])

    @locked_cached_property
    def absolute_jinja_env(self):
        env = Environment(loader=self._absolute_jinja_loader)

        return env


class RestBlueprint(AbsoluteJinjaEnvMixin, ContentNegotiationMixin, Blueprint):
    """A REST Blueprint.

    Deriving from :class:`ContentNegotiatingBlueprint`, all HTTPExcptions
    thrown are rendered by the :func:`~RestBlueprint.exception_renderer`."""

    def __init__(self, *args, **kwargs):
        super(RestBlueprint, self).__init__(*args, **kwargs)

        self.http_errorhandlers(self.__serializing_errorhandler)

        self.content_renderer = renderers.content_renderer
        self.exception_renderer = renderers.exception_renderer

    def http_errorhandlers(self, f):
        """Allow registering a function for all HTTPExceptions.

        This function will go away as soon as the issue in flask is fixed."""
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

    def __serializing_errorhandler(self, exc):
        content_type = get_best_mimetype()

        if not content_type:
            # we found no acceptable content-type to render the exception
            # return nothing but the code
            code = getattr(exc, 'code', 500)
            return make_response(
                '', code, {}
            )

        return self.exception_renderer.render_response(exc, content_type)
