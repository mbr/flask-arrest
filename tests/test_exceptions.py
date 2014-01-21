import json
import pytest
import re

from flask import Flask, abort
from flask_arrest import RestBlueprint


@pytest.fixture
def app():
    app = Flask('exc_testapp')
    return app


@pytest.fixture
def api(app):
    api = RestBlueprint('api', __name__)
    app.testing = True

    @api.route('/throw/<int:code>/', methods=['GET', 'POST'])
    def accepts_foo(code):
        abort(code)

    api.outgoing.set_mimetypes(['text/html', 'text/plain', 'application/json'])

    app.register_blueprint(api)

    return api


# FIXME: app, api, client copy&pasted from test_contentnegotiation, should go
#        into shared file really
@pytest.fixture
# init api to complete the app!
def client(app, api):
    return app.test_client()


def test_unacceptable(client):
    resp = client.get('/throw/403/', headers={
        'Accept': 'something/entirely_unacceptable'
    })
    assert resp.status_code == 403
    assert not resp.data


def test_plain_text_exception(client):
    resp = client.get('/throw/403/', headers={
        'Accept': 'text/plain'
    })
    assert resp.status_code == 403
    assert resp.content_type.startswith('text/plain')


def test_html_exception(client):
    resp = client.get('/throw/403/', headers={
        'Accept': 'text/html'
    })

    assert resp.status_code == 403
    assert resp.content_type.startswith('text/html')
    assert '<html' in resp.data


def test_json_exception(client):
    resp = client.get('/throw/403/', headers={
        'Accept': 'application/json'
    })

    assert resp.status_code == 403
    assert re.match('application/(.*\+)json', resp.content_type)
    data = json.loads(resp.data)

    assert 'type' in data
    assert 'title' in data
