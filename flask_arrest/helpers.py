from flask import current_app, request
from werkzeug.local import LocalProxy


current_blueprint = LocalProxy(
    lambda: current_app.blueprints[request.blueprint]
)


def render_exception_template(template_name_or_list, **context):
    tpl = current_blueprint.exception_jinja_env.get_or_select_template(
        template_name_or_list
    )
    return tpl.render(context)


def get_best_mimetype():
    """Returns the highest quality mimetype-string that client and server can
    agree on. Returns ``None``, if no suitable type is found."""
    # find out what the client accepts
    return request.accept_mimetypes.best_match(
        current_blueprint.response_mimetypes.keys()
    )
