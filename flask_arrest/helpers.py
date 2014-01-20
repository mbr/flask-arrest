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
