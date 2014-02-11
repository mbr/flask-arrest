from __future__ import absolute_import

from copy import deepcopy
from flask import make_response, current_app

# encoding to be used when sending text/plain
TEXT_PLAIN_ENCODING = 'utf8'


class Renderer(object):
    """Basic Renderer interface.

    A Renderer can be asked to render an an object into a response."""
    def render_response(self, data, content_type, status=200):
        """Render data.

        :param data: The data to be rendered.
        :param content_type: A string describing the desired output
                             content-type.
        :param status: The status code for the response.
        :return: A :class:`~flask.Response` instance."""
        raise NotImplementedError


class PluggableRenderer(Renderer):
    """Support rendering content by registering rendering functions for each
    content type.

    Any renderer will be called with arguments matching ``data, content_type``,
    where ``data`` is the object to be rendered and ``content_type`` the
    desired content-type as a string. The return value is passed as arguments
    to :func:`~flask.make_response`.
    """
    def __init__(self, *args, **kwargs):
        super(PluggableRenderer, self).__init__(*args, **kwargs)
        self.content_funcs = {}

    def register_renderer(self, content_type, func):
        """Set renderer for ``content_type`` to func."""
        self.content_funcs[content_type] = func

    def renders(self, content_type):
        """A function decorator. Decorating a function with this is equivalent
        to calling ``register_renderer(content_type, this_function)``.
        """
        def _(f):
            self.register_renderer(content_type, f)
            return f
        return _

    def render_response(self, data, content_type, status=200):
        if not content_type in self.content_funcs:
            raise KeyError('Content-type %r not registered for %r' % (
                content_type, self
            ))

        return make_response(
            self.content_funcs[content_type](data, content_type)
        )

    def copy(self):
        return deepcopy(self)


content_renderer = PluggableRenderer()
exception_renderer = PluggableRenderer()


import json
from pprint import pformat

from flask_arrest.helpers import current_blueprint


@content_renderer.renders('application/json')
def render_json_content(data, content_type, status):
    return json.dumps(data), status, {'Content-type': content_type}


@content_renderer.renders('text/plain')
def render_text_plain_content(data, content_type, status):
    return pformat(data), status, {'Content-type': 'text/plain; charset=ascii'}


@exception_renderer.renders('text/plain')
def render_text_plain_exception(exc, content_type):
    # renders an exception as ascii text
    text = exc.description.encode(TEXT_PLAIN_ENCODING)

    return text, exc.code, {'Content-type': 'text/plain; charset=utf8'}


@exception_renderer.renders('text/html')
def text_html(exc, content_type):
    tpl_name = current_app.config.get('EXCEPTION_TEMPLATE_TEXT_HTML',
                                      'exception.html')
    tpl = current_blueprint.absolute_jinja_env.get_or_select_template(tpl_name)
    html = tpl.render(exc=exc)

    return html, exc.code, {'Content-type': 'text/html; charset=utf8'}


@exception_renderer.renders('application/problem+json')
@exception_renderer.renders('application/json')
def application_problem_json(exc, content_type):
    data = {
        'type': ('https://en.wikipedia.org/wiki/List_of_HTTP_status_codes#%d'
                 % exc.code),
        'title': exc.name,
        'status': exc.code,
        'detail': exc.description,
    }

    return json.dumps(data), exc.code, {'Content-type':
                                        'application/problem+json'}
