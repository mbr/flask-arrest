from flask import make_response


class Renderer(object):
    def render_response(self, data, content_type):
        raise NotImplementedError

    def render_exception(self, exc, content_type):
        # FIXME: this is probably a good idea to add later
        pass


class PluggableRenderer(Renderer):
    def __init__(self, *args, **kwargs):
        super(PluggableRenderer, self).__init__(*args, **kwargs)
        self.render_funcs = {}

    def register_func(self, content_type, func):
        self.render_funcs[content_type] = func

    def renders_content(self, content_type):
        def _(f):
            self.register_func(content_type, f)
            return f
        return _

    def render_response(self, data, content_type):
        if not content_type in self.render_funcs:
            raise KeyError('Content-type %r has not been registered on %r' % (
                content_type, self
            ))

        return make_response(
            self.render_funcs[content_type](data, content_type)
        )


default_renderer = PluggableRenderer()

import json
from pprint import pformat


@default_renderer.renders_content('application/json')
def render_json_content(data, content_type):
    return json.dumps(data)


@default_renderer.renders_content('text/plain')
def render_text_plain_content(data, content_type):
    return pformat(data)
