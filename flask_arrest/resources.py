from flask import request
from flask.views import View
import werkzeug
from werkzeug.exceptions import NotFound

from . import serialize_response
from .helpers import register_converter


class ResourceView(View):
    VIEW_DELIM = ':'

    def __init__(self, handler):
        self.handler = handler

    def dispatch_request(self, *args, **kwargs):
        action = getattr(self.handler,
                         self.extract_endpoint_target(request.endpoint))
        return serialize_response(action(*args, **kwargs))

    @classmethod
    def construct_endpoint(cls, handler, target,
                           methods, uri_template, override=None):
        if override:
            return override.format(handler)
        return handler.singular + cls.VIEW_DELIM + target

    @classmethod
    def extract_endpoint_target(cls, name):
        if cls.VIEW_DELIM in name:
            return name.rsplit(cls.VIEW_DELIM, 1)[1]
        else:
            # no VIEW_DELIM in endpoint name, default to show
            return 'show'


class HandlerMixin(object):
    uris = {
        'show': (['GET'], '/{0.singular}/<{0.singular}:obj_id>/',
                 '{0.singular}'),
        'create': (['POST'], '/{0.plural}/'),
        'update': (['PATCH'], '/{0.singular}/<{0.singular}:obj_id>/'),
        'replace': (['PUT'], '/{0.singular}/<{0.singular}:obj_id>/'),
        'remove': (['DELETE'], '/{0.singular}/<{0.singular}:obj_id>/'),
        'query': (['GET'], '/{0.plural}/'),
    }

    def _obj_to_id(self, obj):
        return str(obj.id)

    def show(self, obj_id):
        try:
            obj = self._from_id(obj_id)
        except (ValueError, KeyError):
            raise NotFound()
        return obj


def mount_resource(app_or_blueprint, handler):
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
            return handler._obj_to_id()

    register_converter(app_or_blueprint, handler.singular, Converter)

    # note: we use getattr instead of hasattr to allow classes to override
    #       methods they don't want with None to hide them
    for target, data in handler.uris.items():
        name = ResourceView.construct_endpoint(handler, target, *data)

        if getattr(handler, target, None):
            app_or_blueprint.add_url_rule(
                data[1].format(handler),
                view_func=ResourceView.as_view(name, handler),
                methods=data[0])
