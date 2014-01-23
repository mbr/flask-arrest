from flask import request
from flask.views import View
from werkzeug.exceptions import NotFound

from .helpers import serialize_response


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
