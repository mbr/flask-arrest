Example usage
=============

.. code-block:: python

   from flask import abort, request
   from flask.ext.arrest import RestBlueprint

   restapi = RestBlueprint('restapi', __name__)  # use like a regular blueprint

   # optional: support custom content-types. otherwise, application/json is the
   #           default. if no serializer is supplied, will use the default
   #           serialzer, which is a specialized JSONSerializer.
   restapi.add_response_type('application/vnd.myapp+json')
   restapi.add_request_type('application/vnd.myapp+json')

   @restapi.route('/the-menu/')
   def index():
     # For the _links-keys, see http://stateless.co/hal_specification.html
     our_menu = {
       'beverages': [
         {
           'name': 'coffee',
           'price': 2.00,
           'description': 'Our house-blend of charcoal and tar, with cream.',
           '_links': {
             'order': url_for('.order', id='coffee'),
             'self': url_for('.detailed_info', id='coffee'),
           }
         }, {
           'name': 'tea',
           'price': 2.50,
           'description': 'Made from organic tobacco and maple leafs.',
           '_links': {
             'order': url_for('.order', id='tea'),
             'self': url_for('.detailed_info', id='tea'),
           },
         },
      ]
    }

    # usually, you may want to populate the menu from a model/database
    # containing whats on sale
    return our_menu

  @restapi.route('/coffee-shop/order/<id>/', methods=['POST'])
  def order(id):
    if not id in ('coffee', 'tea'):
      # use regular Flask aborts to return error messages, these will be
      # serialized to a format the client does accept (in this case, JSON).
      abort(404, 'We do not serve these things here, sorry.')

    d = request.parsed_data
    # d now contains the request data, parsed using the parser set above or the
    # default of the JSON-parser.

    # .. process

    # any dict will automatically be serialized.
    return some_response

  # omitted: function detailed_info


A justification for its existance
=================================
Flask-arrest is a simple extension to ease the development of REST-applications.
This code isn't necessarily meant for public consumption, use at your own risk.
Feedback of any kind, however, is very welcome.

The following other Flask extensions are avaible for REST-functionality, they
have been considered before creating this extension:

* `Flask-Restless <http://flask-restless.readthedocs.org/en/latest/>`_, does
  solve a slightly different problem, with fairly tight coupling.
* `Flask-REST <https://github.com/ametaireau/flask-rest/>`_. Best name, no
  longer under development (at the time of this writing, hasn't been for two
  years). Usage seems fairly clumsy with a lot of classes being thrown around.
* `Flask-Restful <http://flask-restful.readthedocs.org/en/latest/>`_ seems to
  be the best of the bunch. Cute kitten in docs. Active development. Many
  contributors. Lots of docs and apparently production usage/testing.

So why not use Flask-Restful? The following points describe what Flask-arrest
tries to do better:

* Being Flask-y. Using classes instead of decorated function for routes looks
  fairly alien in a Flask application, yet all other extensions seem to want to
  force this for the obvious OO-abstraction. Flask-arrest uses routes, the
  ``methods`` parameter and, if desirable, an ``if request.method ==`` statement
  for the same purpose. This means no new code and no new idioms (e.g. url_for
  just works), everything instantly recognizable by experienced (and novice)
  Flask-developers.
* Use Blueprints. Should be a part of "being Flask-y" (see above), but is
  important enough to warrant its own mention. Again, saves code, makes stuff
  recognizable instantly and uses well-known Flask idioms. Also allows easily
  putting the API endpoints onto the app with any prefix.

In addition, it should be possible to easily implement the three levels of REST-
Apis. All the mentioned REST-extensions seem to go up only to level 2, stopping
short of Hypermedia Controls (HATEOAS); at the very least they are not including
them in examples. Another missing feature ("missing" not meaning impossible-to-
do, but not a first-class feature) seems to be  Content-Negotiation, especially
if unconventional or vendor-specific Content-Types are desired.


State of the library
====================

The current library is the result of a bit of research on REST, a little
experimentation with Flask features and a bit of planning. I am using it in two
projects and will make corrections if things don't "feel" right. If you wish to
use this library elsewhere, go ahead. You may want to let me know as well, as
this will cause me to be a little more careful about breaking things.
