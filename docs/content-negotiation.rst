Content-negotiation
===================

Content-negotiation is, in case of Flask-arrest, accepting only content-types
that a server can process and serving the client only representations of data
that it can understand.


A simple example
----------------

.. code-block:: python

   from flask_arrest import RestBlueprint, serialize_response

   api = RestBlueprint('api', __name__)

   # for outgoing data, the app additionally supports CSV in addition to
   # application/json
   api.outgoing.add_mimetype('text/csv')


   @api.content_renderer.renders('text/csv')
   def render_csv(data):
       """Given any temperature data, this function returns a CSV-string of it"""
       # ...


   @api.route('/temperatures/', methods=['POST'])
   def upload_data():
       """Processes uploaded temperatures and adds the to the database."""
       # ...

   @api.route('/temperatures/', methods=['GET'])
   def query_temperatures():
       """Allows querying tepmperature records."""

       # we use static fixtures in this example
       temps = [
           {'measured': DateTime(2014, 02, 04, 17, 38),
            'temperature': 6},
           {'measured': DateTime(2014, 02, 04, 19, 12),
            'temperature': 4}
       ]

       # render the data for a specific content-type. if no content-type is
       # given, the best (according to client-preference) type registered
       # (see api.outgoing) will be delivered
       return serialize_response(temps)

The (incomplete) application above supports one incoming mimetype and two
outgoing ones (``application/json`` is the overridable default in both cases,
see :py:attr:`~flask_arrest.ContentNegotiationMixin.incoming` and
:py:attr:`~flask_arrest.ContentNegotiationMixin.outgoing`). This allows the
client to specify his preferred format for receiving data using `HTTP headers
<https://en.wikipedia.org/wiki/List_of_HTTP_headers>`_.

Content-negotiation is handled automatically by any
:py:class:`~flask.Blueprint` that has the
:py:class:`~flask_arrest.ContentNegotiationMixin` mixed in.

.. digraph:: foo

   req [shape=box, style=filled, label="Incoming Request"];
   resp [shape=box, style=filled, label="Outgoing Response"];
   bp [label="ContentNeg Blueprint"]
   exc_ren [label="Exception Renderer", color=blue]
   con_ren [label="Content Renderer", color=blue]
   exc [label="Unhandled Exceptions", shape=box]
   view [label="View function"]

   req -> bp;
   bp -> exc_ren [label="UnsupportMediaType?"]
   bp -> view
   view -> con_ren [label="serialize_response()", fontname="Monospace"]
   view -> exc_ren [label="raise HTTPError", fontname="Monospace"]

   exc -> exc_ren [label="HTTP500"]
   exc_ren -> resp [label="Renders acceptable response"]
   exc_ren -> resp [label="Falls back to HTML/HTTP415", color=red,
                    fontcolor=red]
   con_ren -> resp [label="Renders acceptable response"]


Incoming content
----------------

Data is sent to the server from the client only with specific HTTP methods
(usually, these are ``POST``, ``PUT`` and ``PATCH`` for basic HTTP). Clients
are required to include a ``Content-type`` header in these requests,
specifying the mimetype of the data sent.

When a request arrives at a :py:class:`~flask_arrest.ContentNegotiationMixin`
derived :py:class:`~flask.Blueprint`, its ``Content-type``-header is matched
against any :py:attr:`~flask_arrest.ContentNegotiationMixin.incoming` type. If
it does not match any of the types registered there, an
:py:class:`~werkzeug.exceptions.UnsupportedMediaType` exception is thrown (and
returned to the client, see `Outgoing content` for a description on how it
will serialized).

If a client does not send a ``Content-type``-header along with the contents,
an :py:class:`~werkzeug.exceptions.UnsupportedMediaType` exception is thrown as
well. If there is no content, the ``Content-type``-header is ignored.

Afterwards, the requests is processed as normal and passed on to a view.


Outgoing content
----------------

Flask-arrest does not alter response automatically, but provides facilities to
do so. These are concentrated in the following two helper functions:

.. autofunction:: flask_arrest.helpers.get_best_mimetype

Normally, you will not need to call
:py:func:`~flask_arrest.helpers.get_best_mimetype` directly, instead interact
with the following function:

.. autofunction:: flask_arrest.helpers.serialize_response


Content-negotiation API reference
---------------------------------

.. autoclass:: flask_arrest.ContentNegotiationMixin
   :members:

.. autoclass:: flask_arrest.helpers.MIMEMap
   :members:
