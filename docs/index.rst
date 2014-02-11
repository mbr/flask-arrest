Flask-arrest
============

Flask-arrest is a `Flask <http://flask.pocoo.org>`_-extension that works hard
to make it easy to implement `REST <http://wikipedia.org/wiki/REST>`_-APIs
using Flask.

.. todo:: there should be a cool code sample here
.. .. code-block:: python
..
..    from flask_arrest import RestBlueprint, serialize_response
..
..    frontend = RestBlueprint('frontend', __name__)
..
..    @frontend.route('/greet/<name>/')
..    def greet(name):
..        return serialize_response({
..            'name': name,
..            'greeting': 'Hello, {0}'.format(name),
..        })
..
..    from flask import Flask
..
..    app = Flask(__name__)
..    app.register_blueprint(frontend)
..
..    app.run(debug=True)


Flask-arrest is very modular and has three key concerns,
*content-negotiation*, *content-serialization/-deserialization* and supporting
*resource abstraction*. Each of these aspects can be replaced with an external
library.

There are other REST-extensions available for Flask, check `other-libraries`
for details.

Conceptual overview
-------------------

Below you find an overview of the complete conceptual path a request takes on
its way of generating a response:

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


.. toctree::
   :maxdepth: 2

   content-negotiation
   rendering
   other-libraries

State of the library
====================

Flask-arrest is still under heavy development at this point. The API underwent
major changes in version 0.4, but do not count on anything being nailed down
100%. Any feedback is very welcome.
