TEXT_PLAIN_ENCODING = 'utf8'

from flask import current_app

from .helpers import render_exception_template

# FIXME: to support problem+json, we probably need to define
#        our own exception class


def text_plain(exc):
    # renders an exception as ascii text
    text = exc.description.encode(TEXT_PLAIN_ENCODING)

    return text, exc.code, {'Content-type': 'text/plain; charset=utf8'}


def text_html(exc):
    tpl_name = current_app.config.get('EXCEPTION_TEMPLATE_TEXT_HTML',
                                      'exception.html')
    html = render_exception_template(tpl_name, exc=exc)

    return html, exc.code, {'Content-type': 'text/html'}
