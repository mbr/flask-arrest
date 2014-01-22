from flask import Flask
from flask_arrest import RestBlueprint

import pytest


@pytest.fixture
def app():
    app = Flask('testapp')
    return app


@pytest.fixture
def api(app):
    api = RestBlueprint('api', __name__)
    app.testing = True  # important, otherwise we won't be seeing exceptions

    @api.route('/accepts-foo/', methods=['GET', 'POST'])
    def accepts_foo():
        return ''

    api.incoming.set_mimetypes(['application/foo'])
    app.register_blueprint(api)

    return api


@pytest.fixture
def simple_api(app):
    api = RestBlueprint('api', __name__)
    app.testing = True

    @api.route('/', methods=['POST'])
    def index():
        return 'OK'

    app.register_blueprint(api)

    return api


@pytest.fixture
def simple_client(app, simple_api):
    return app.test_client()


@pytest.fixture
# init api to complete the app!
def client(app, api):
    return app.test_client()


def test_no_incoming_type(client):
    assert client.post('/accepts-foo/').status_code == 415


def test_acceptable_incoming_type(client):
    assert client.post('/accepts-foo/',
                       headers={'Content-Type': 'application/foo'}
                       ).status_code == 200


def test_unacceptable_incoming_type(client):
    assert client.post('/accepts-foo/',
                       headers={'Content-Type': 'application/bar'}
                       ).status_code == 415


def test_get_incoming_type_with_empty_bodies(client):
    assert client.get('/accepts-foo/').status_code == 200
    assert client.get('/accepts-foo/',
                      headers={'Content-Type': 'application/foo'}
                      ).status_code == 200


# simple client
def test_application_json_default(simple_client):
    assert simple_client.post('/',
                              headers={'Content-Type': 'application/json'}
                              ).status_code == 200
