from flask import make_response, current_app

# encoding to be used when sending text/plain
TEXT_PLAIN_ENCODING = 'utf8'


class Renderer(object):
    def render_response(self, data, content_type):
        raise NotImplementedError


class PluggableRenderer(Renderer):
    def __init__(self, *args, **kwargs):
        super(PluggableRenderer, self).__init__(*args, **kwargs)
        self.content_funcs = {}

    def register_renderer(self, content_type, func):
        self.content_funcs[content_type] = func

    def renders(self, content_type):
        def _(f):
            self.register_renderer(content_type, f)
            return f
        return _

    def render_response(self, data, content_type):
        if not content_type in self.content_funcs:
            raise KeyError('Content-type %r not registered for %r' % (
                content_type, self
            ))

        return make_response(
            self.content_funcs[content_type](data, content_type)
        )


content_renderer = PluggableRenderer()
exception_renderer = PluggableRenderer()

import json
from pprint import pformat


@content_renderer.renders('application/json')
def render_json_content(data, content_type):
    return json.dumps(data), 200, {'Content-type': content_type}


@content_renderer.renders('text/plain')
def render_text_plain_content(data, content_type):
    return pformat(data), 200, {'Content-type': 'text/plain; charset=ascii'}


@exception_renderer.renders('text/plain')
def render_text_plain_exception(exc, content_type):
    # renders an exception as ascii text
    text = exc.description.encode(TEXT_PLAIN_ENCODING)

    return text, exc.code, {'Content-type': 'text/plain; charset=utf8'}


@exception_renderer.renders('text/html')
def text_html(exc, content_type):
    tpl_name = current_app.config.get('EXCEPTION_TEMPLATE_TEXT_HTML',
                                      'exception.html')
    html = render_exception_template(tpl_name, exc=exc)

    return html, exc.code, {'Content-type': 'text/html; charset=utf8'}


@exception_renderer.renders('application/problem+json')
@exception_renderer.renders('application/json')
def application_problem_json(exc, content_type):
    # FIXME: to support problem+json properly, we probably need to define
    #        our own exception class?

    data = {
        'type': ('https://en.wikipedia.org/wiki/List_of_HTTP_status_codes#%d'
                 % exc.code),
        'title': exc.name,
        'status': exc.code,
        'detail': exc.description,
    }

    return json.dumps(data), exc.code, {'Content-type':
                                        'application/problem+json'}
