from collections import defaultdict

from flask import current_app, request
from werkzeug.local import LocalProxy


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


def get_best_mimetype():
    """Returns the highest quality server-to-client content-type that both
    agree on. Returns ``None``, if no suitable type is found.

    Internally, works by querying the blueprint for its
    :attr:`~flask_arrest.Blueprint.outgoing` attribute and comparing it with
    the ``Accept``-headers sent by the client.."""
    # find out what the client accepts
    return request.accept_mimetypes.best_match(
        current_blueprint.outgoing.get_mimetypes(request.endpoint)
    )


class MIMEMap(object):
    """A MIMEMap is a special datastructure that maps an endpoint to a set of
    mimetypes. The default value of any endpoint not found is ``set([None])``.
    A value of ``None`` will be replaced with all mimetypes set for the default
    set of mimetypes, which are configurable by using ``None`` as the endpoint
    name."""
    def __init__(self):
        self._map = defaultdict(lambda: set([None]))

    def add_mimetype(self, mimetype, endpoint=None):
        """Adds a mimetype to and endpoint."""
        if mimetype is None and endpoint is None:
            raise ValueError('Cannot add default mimetype on default.')

        self._map[endpoint].add(mimetype)

    def set_mimetypes(self, mimetypes, endpoint=None):
        """Sets all mimetypes for an endpoint.

        Note that if you exclude ``None`` from the ``mimetypes`` parameter,
        the defaults will not be applied."""
        if endpoint is None and None in mimetypes:
            raise ValueError('Cannot include default mimetype in default.')

        self._map[endpoint] = set(mimetypes)

    def get_mimetypes(self, endpoint=None):
        """Get all mimetypes for an endpoint."""
        mimetypes = set(self._map[endpoint])

        if None in mimetypes:
            mimetypes.update(self._map[None])
            mimetypes.remove(None)

        return mimetypes
