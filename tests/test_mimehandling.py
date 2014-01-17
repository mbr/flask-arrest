from flask_arrest import RestBlueprint

import pytest


@pytest.fixture
def apibp():
    bp = RestBlueprint('apipb', __name__)

    return bp


def test_default_is_json(apibp):
    assert apibp.get_accepted_mimetypes() == set(['application/json'])


def test_default_for_arbitrary_endpoint_is_json(apibp):
    assert apibp.get_accepted_mimetypes('some-endpoint') ==\
        set(['application/json'])


def test_setting_default_mimetypes(apibp):
    apibp.set_accepted_mimetypes(['application/x', 'application/y'])

    assert apibp.get_accepted_mimetypes() ==\
        set(['application/x', 'application/y'])


def test_add_default_mimetypes(apibp):
    apibp.add_accepted_mimetype('application/new')

    assert apibp.get_accepted_mimetypes() ==\
        set(['application/json', 'application/new'])


def test_arbitrary_endpoint_mimetype_default(apibp):
    assert apibp.get_accepted_mimetypes('some_nonexisting_endpoint') ==\
        set(['application/json'])


def test_adding_to_endpoint(apibp):
    apibp.add_accepted_mimetype('application/z', 'endpointx')

    assert apibp.get_accepted_mimetypes('endpointx') ==\
        set(['application/json', 'application/z'])


def test_disabling_default_acceptance(apibp):
    apibp.set_accepted_mimetypes(['application/only'], 'endpointy')

    assert apibp.get_accepted_mimetypes('endpointy') ==\
        set(['application/only'])


def test_adding_none_allowed_for_endpoints(apibp):
    apibp.add_accepted_mimetype(None, 'endpoint')


def test_adding_none_not_allow_for_root(apibp):
    with pytest.raises(ValueError):
        apibp.add_accepted_mimetype(None)
