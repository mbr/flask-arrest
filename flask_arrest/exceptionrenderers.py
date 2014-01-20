import json

from flask import current_app

from .helpers import render_exception_template

TEXT_PLAIN_ENCODING = 'utf8'


def text_plain(exc):
    # renders an exception as ascii text
    text = exc.description.encode(TEXT_PLAIN_ENCODING)

    return text, exc.code, {'Content-type': 'text/plain; charset=utf8'}


def text_html(exc):
    tpl_name = current_app.config.get('EXCEPTION_TEMPLATE_TEXT_HTML',
                                      'exception.html')
    html = render_exception_template(tpl_name, exc=exc)

    return html, exc.code, {'Content-type': 'text/html; charset=utf8'}


def application_problem_json(exc):
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
