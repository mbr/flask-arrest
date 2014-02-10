from collections import defaultdict

from flask import current_app, request
from flask.helpers import _endpoint_from_view_func
from werkzeug.local import LocalProxy
from werkzeug.exceptions import NotAcceptable


current_blueprint = LocalProxy(
    lambda: current_app.blueprints[request.blueprint]
)


def register_converter(app_or_blueprint, name, converter):
    """Registers a converter on a url_map of an app or adds it to a blueprint.
    """

    # the following is a helper to register a converter through a blueprint
    def _register_converter(app):
        app.url_map.converters[name] = converter

    # attach directly if called on app, through blueprint otherwise
    if hasattr(app_or_blueprint, 'url_map'):
        _register_converter(app_or_blueprint)
    else:
        app_or_blueprint.record_once(
            lambda state: _register_converter(state.app)
        )


def serialize_response(response_data, content_type=None, renderer=None):
    """Serializes a response using a specified renderer.

    This will serialize ``response_data`` with the specified ``content_type``,
    using ``renderer``.

    If ``content_type`` is ``None``,
    :py:func:`~flask_arrest.helpers.get_best_mimetype` will be used to
    determine a suitable type. If no match is found, a
    :py:class:`~werkzeug.exceptions.NotAcceptable` exception is thrown.

    If no render is supplied, use the blueprint's
    :attr:`~flask_arrest.RestBlueprint.content_renderer`.

    :param response_data: Data to be serialized. Can be anything the serializer
                          can handle.
    :param content_type: The ``Content-type`` to serialize for.
    :param renderer: The renderer to use. If ``None``, lookup the current
                     blueprint's
                     :attr:`~flask_arrest.RestBlueprint.content_renderer`.
    :return: A :class:`~flask.Response` object."""
    content_type = content_type or get_best_mimetype()

    if not content_type:
        # no accepted content-type. send flasks default 406, instead of raising
        return NotAcceptable()

    if not renderer:
        renderer = current_blueprint.content_renderer
    return renderer.render_response(response_data, content_type)


def get_best_mimetype():
    """Returns the highest quality server-to-client content-type that both
    agree on. Returns ``None``, if no suitable type is found.

    Internally, works by querying the blueprint for its
    :attr:`~flask_arrest.ContentNegotiationMixin.outgoing` attribute and
    comparing it with the ``Accept``-headers sent by the client.."""
    # find out what the client accepts
    return request.accept_mimetypes.best_match(
        current_blueprint.outgoing.get_mimetypes(request.endpoint)
    )


class MIMEMap(object):
    """Special datastructure that maps an endpoint to a set of mimetypes. The
    default set of mimetypes for any endpoint is ``{None}``.

    A value of ``None`` will be replaced with all mimetypes set for the
    special endpoint
    :py:const:`~flask_arrest.helpers.MIMEMap.DEFAULT_ENDPOINT`.

    If ``None`` is *not* included in a specific endpoints set of mimetypes, it
    will not include the defaults mentioned above.

    Note that endpoint names should usually be added without the
    Blueprint-prefix (i.e. "index" instead of "api.index").
    """

    #: The default endpoint. Any value of ``None`` in the set of acceptable
    #: types in other endpoints will be replaced with all types assigned to
    #: this endpoint.
    DEFAULT_ENDPOINT = None

    def __init__(self):
        self._map = defaultdict(lambda: set([None]))

    def add_mimetype(self, mimetype, endpoint=DEFAULT_ENDPOINT):
        """Adds a mimetype to an endpoint."""
        if mimetype is None and endpoint is self.DEFAULT_ENDPOINT:
            raise ValueError('Cannot add default mimetype on default.')

        self._map[endpoint].add(mimetype)

    def set_mimetypes(self, mimetypes, endpoint=DEFAULT_ENDPOINT):
        """Sets all mimetypes for an endpoint.

        Note that if you exclude ``None`` from the ``mimetypes`` set, the
        mimetypes set for
        :py:const:`~flask_arrest.helpers.MIMEMap.DEFAULT_ENDPOINT` will not be
        applied. This allows specifying an endpoint that does not handle all
        of the otherwise common mimetypes."""
        if endpoint is self.DEFAULT_ENDPOINT and None in mimetypes:
            raise ValueError('Cannot include default mimetype in default.')

        self._map[endpoint] = set(mimetypes)

    def get_mimetypes(self, endpoint=DEFAULT_ENDPOINT):
        """Get all mimetypes for an endpoint."""
        mimetypes = set(self._map[endpoint])

        if None in mimetypes:
            mimetypes.update(self._map[None])
            mimetypes.remove(None)

        return mimetypes

    def accepts(self, extra_type):
        def _(f):
            self.add_mimetype(extra_type, _endpoint_from_view_func(f))
            return f
        return _

    def accepts_only(self, only_types):
        def _(f):
            self.set_mimetypes(only_types, _endpoint_from_view_func(f))
            return f
        return _
