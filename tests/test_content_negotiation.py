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
# init api to complete the app!
def client(app, api):
    return app.test_client()


def test_no_content_type(client):
    assert client.post('/accepts-foo/').status_code == 415


def test_acceptable_content_type(client):
    assert client.post('/accepts-foo/',
                       headers={'Content-Type': 'application/foo'}
                       ).status_code == 200


def test_unacceptable_content_type(client):
    assert client.post('/accepts-foo/',
                       headers={'Content-Type': 'application/bar'}
                       ).status_code == 415


def test_get_content_type_with_empty_bodies(client):
    assert client.get('/accepts-foo/').status_code == 200
    assert client.get('/accepts-foo/',
                      headers={'Content-Type': 'application/foo'}
                      ).status_code == 200
