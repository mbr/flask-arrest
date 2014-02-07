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

.. toctree::
   :maxdepth: 2

   other-libraries

State of the library
====================

Flask-arrest is still under heavy development at this point. The API underwent
major changes in version 0.4, but do not count on anything being nailed down
100%. Any feedback is very welcome.
