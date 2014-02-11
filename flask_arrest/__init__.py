#!/usr/bin/env python

from flask import Blueprint, request, abort, make_response
from flask.helpers import locked_cached_property
from jinja2 import PackageLoader, ChoiceLoader, Environment
import werkzeug

from .helpers import get_best_mimetype, MIMEMap, register_converter
from .resources import ResourceView
from . import renderers

__version__ = '0.3.dev2'


class ContentNegotiationMixin(object):
    """A blueprint mixin that supports content negotiation. Used in conjunction
    with the :func:`get_best_mimetype()` and :func:`serialize_response()`
    functions.

    :attr:`~flask_arrest.ContentNegotiationMixin.incoming` types are checked
    whenever a client sends a request with content to this blueprint. If the
    supplied ``Content-type``-Header is not among the MIME-Types valid for
    the specific endpoint, the request is rejected with a
    :py:class:`~werkzeug.exceptions.UnsupportedMediaType` exception.

    :attr:`~flask_arrest.ContentNegotiationMixin.outgoing` types supply
    information about which possible mimetypes can be sent back to the client.
    Renderers for data can use these to find an intersection with the
    ``Accept``-headers the client sent. Many will send an HTTP 406 (Not
    Acceptable) error if none of the advertised types is found in the clients
    ``Accept``-header."""

    def __init__(self, *args, **kwargs):
        super(ContentNegotiationMixin, self).__init__(*args, **kwargs)
        self.before_request(self.__check_incoming_content_type)

        self.incoming = MIMEMap()
        """a :py:class:`~flask_arrest.helpers.MIMEMap` of incoming data types.
        The default will contain just ``application/json``."""

        self.incoming.add_mimetype('application/json')

        self.outgoing = MIMEMap()
        """a :py:class:`~flask_arrest.helpers.MIMEMap` of outgoing data types.
        The default will contain just ``application/json``."""
        self.outgoing.add_mimetype('application/json')

    def __check_incoming_content_type(self):
        if not request.content_type and (request.data or request.form):
            abort(415)  # client needs to send a content-type, if he sends
                        # content

        if not request.content_type and not (request.data or request.form):
            return  # no content, no problem

        # strip the blueprint prefix
        prefix = self.name + '.'
        if request.endpoint.startswith(prefix):
            endpoint_name = request.endpoint[len(prefix):]
        else:
            endpoint_name = request.endpoint
        accepted = self.incoming.get_mimetypes(endpoint_name)
        if not request.content_type in accepted:
            abort(415)


class AbsoluteJinjaEnvMixin(object):
    """Jinja environment helper mixin.

    Creates a separate jinja_env for temlates that come bundled with a
    blueprint (when deriving from a blueprint, normally the template_path will
    be overridden).
    """
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


# FIXME: this may or may not be removed
class ResourceMountMixin(object):
    def mount_resource(self, handler):
        # NOTE: we are not using converters to unmarshal right now - exceptions
        #       triggered by loading resources through converters will not
        #       get handled by the blueprint exception handlers. this may
        #       or may not be possible to remedy by registering application-
        #       wide exceptions handlers
        #
        # create a converter for handler
        class Converter(werkzeug.routing.BaseConverter):
            def to_python(self, value):
                return value

            def to_url(self, obj):
                return handler._obj_to_id(obj)

        register_converter(self, handler.singular, Converter)

        # note: we use getattr instead of hasattr to allow classes to override
        #       methods they don't want with None to hide them
        for target, data in handler.uris.items():
            name = ResourceView.construct_endpoint(handler, target, *data)

            if getattr(handler, target, None):
                self.add_url_rule(
                    data[1].format(handler),
                    view_func=ResourceView.as_view(name, handler),
                    methods=data[0])


class RestBlueprint(AbsoluteJinjaEnvMixin, ContentNegotiationMixin,
                    ResourceMountMixin, Blueprint):
    """A REST Blueprint."""

    def __init__(self, *args, **kwargs):
        super(RestBlueprint, self).__init__(*args, **kwargs)

        self.http_errorhandlers(self.__serializing_errorhandler)

        self.content_renderer = renderers.content_renderer.copy()
        """The content renderer to use as the default. Usually called by
        :py:func:`~flask_arrest.helpers.serialize_response`, should support
        the :py:class:`~flask_arrest.renderers.Renderer` interface.

        Per default, a copy of
        :py:attr:`~flask_arrest.renderers.content_renderer` is used as the
        initial value."""

        self.exception_renderer = renderers.exception_renderer.copy()
        """The exception renderer that is used to render every
        :py:class:`~werkzeug.exceptions.HTTPException` thrown inside this
        blueprint. Should  support the
        :py:class:`~flask_arrest.renderers.Renderer` interface."""

    def http_errorhandlers(self, f):
        """Decorator for registering a function as an exception handler
        for all instances of :py:class:`~werkzeug.exceptions.HTTPException`.

        This function will go away as soon as the following
        issue in flask is fixed: https://github.com/mitsuhiko/flask/pull/952"""
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
