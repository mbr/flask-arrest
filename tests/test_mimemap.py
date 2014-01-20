from flask_arrest.helpers import MIMEMap

import pytest


@pytest.fixture
def m():
    return MIMEMap()


def test_empty_map(m):
    assert m.get_mimetypes('foo') == set([None])
    assert m.get_mimetypes('bar') == set([None])


def test_adding_mimetype(m):
    m.add_mimetype('app/foo', 'bar')
    assert m.get_mimetypes('bar') == set([None, 'app/foo'])


def test_setting_mimetypes(m):
    m.set_mimetypes(['app/bar'], 'ep')
    assert m.get_mimetypes('ep') == set(['app/bar'])


def test_defaults_included(m):
    m.set_mimetypes(['a', 'b'], None)
    m.add_mimetype('c', 'foo')
    assert m.get_mimetypes() == set(['a', 'b'])
    assert m.get_mimetypes('foo') == set(['a', 'b', 'c'])


def test_adding_none_to_none(m):
    with pytest.raises(ValueError):
        m.add_mimetype(None)


def test_setting_none_to_none(m):
    with pytest.raises(ValueError):
        m.set_mimetypes(['a', 'b', None])
