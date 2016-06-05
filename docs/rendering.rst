Renderers
=========

Quick use
~~~~~~~~~
Similar to :func:`json.dumps`, the extended encoding capabilities can be used
like this::

    import flask_arrest.json as extjson

    extjson.dumps('foo')


Rendering and content negotiation
---------------------------------

To transform data into a representation, a
:py:class:`~flask_arrest.renderers.Renderer` is required. Flask-arrest
distinguishes between two renderers: Content renderers and exception renderers.

Content-renderers are usually invoked by
:py:func:`~flask_arrest.helpers.serialize_response` and turn arbitrary data
into a content-type they can handle. If not content-renderer is supplied in the
function call, the :py:attr:`~flask_arrest.RestBlueprint.content_renderer`
attribute will be used.

If an exception occurs, it is rendered by a different renderer:
:py:attr:`~flask_arrest.RestBlueprint.exception_renderer`. While the interface
is the same, it is usually not directly invoked by view code; instead any
instance of :py:class:`~werkzeug.exceptions.HTTPException` inside a
:py:class:`~flask_arrest.RestBlueprint` is passed to it automatically instead.


Rendering API reference
-----------------------

.. autoclass:: flask_arrest.renderers.Renderer
   :members:

.. autoclass:: flask_arrest.renderers.PluggableRenderer
   :members:

.. data:: flask_arrest.renderers.content_renderer

    The default content rendererer, includes preset renderers for
    ``application/json`` and ``text/plain``. JSON data is handled by a simple
    :func:`flask_arrest.json.dumps`, while text-rendering is performed by
    :func:`pprint.pformat`. See the source code for details.

.. data:: flask_arrest.renderers.exception_renderer

    The default exception renderer, renders exception as ``application/json``,
    ``application/problem+json`` (the `Problem Details for HTTP APIs
    <https://tools.ietf.org/html/draft-nottingham-http-problem>`_-format),
    ``text/plain`` and ``text/html``.
