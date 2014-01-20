from flask_arrest import RestBlueprint

import pytest


@pytest.fixture
def apibp():
    bp = RestBlueprint('apipb', __name__)

    return bp


def test_default_is_json(apibp):
    assert apibp.incoming.get_mimetypes() == set(['application/json'])


def test_default_for_arbitrary_endpoint_is_json(apibp):
    assert apibp.incoming.get_mimetypes('some-endpoint') ==\
        set(['application/json'])


def test_setting_default_mimetypes(apibp):
    apibp.incoming.set_mimetypes(['application/x', 'application/y'])

    assert apibp.incoming.get_mimetypes() ==\
        set(['application/x', 'application/y'])


def test_add_default_mimetypes(apibp):
    apibp.incoming.add_mimetype('application/new')

    assert apibp.incoming.get_mimetypes() ==\
        set(['application/json', 'application/new'])


def test_arbitrary_endpoint_mimetype_default(apibp):
    assert apibp.incoming.get_mimetypes('some_nonexisting_endpoint') ==\
        set(['application/json'])


def test_adding_to_endpoint(apibp):
    apibp.incoming.add_mimetype('application/z', 'endpointx')

    assert apibp.incoming.get_mimetypes('endpointx') ==\
        set(['application/json', 'application/z'])


def test_disabling_default_acceptance(apibp):
    apibp.incoming.set_mimetypes(['application/only'], 'endpointy')

    assert apibp.incoming.get_mimetypes('endpointy') ==\
        set(['application/only'])


def test_adding_none_allowed_for_endpoints(apibp):
    apibp.incoming.add_mimetype(None, 'endpoint')


def test_adding_none_not_allow_for_root(apibp):
    with pytest.raises(ValueError):
        apibp.incoming.add_mimetype(None)
