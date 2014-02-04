Other libraries
===============

The following other Flask extensions are avaible for REST-functionality, they
have been considered before creating this extension:

* `Flask-Restless <http://flask-restless.readthedocs.org/en/latest/>`_, does
  solve a slightly different problem, with fairly tight coupling.
* `Flask-REST <https://github.com/ametaireau/flask-rest/>`_. Best name, no
  longer under development (at the time of this writing, hasn't been for two
  years). Usage seems fairly clumsy with a lot of classes being thrown around.
* `Flask-Restful <http://flask-restful.readthedocs.org/en/latest/>`_ seems to
  be the best of the bunch and in active development with many contributors.
  Lots of docs and apparently production usage/testing.

So why not use Flask-Restful? The following points describe what Flask-arrest
tries to do better than Flask-Restful:

* Being Flask-y. Using classes instead of decorated function for routes looks
  fairly alien in a Flask application, yet all other extensions seem to want
  to force this for the obvious OO-abstraction. Flask-arrest uses routes,
  view, the ``methods`` parameter. This means no new code and no new idioms
  (e.g. url_for just works), everything instantly recognizable by experienced
  (and novice) Flask-developers.
* Using Blueprints. Should be a part of "being Flask-y" (see above), but is
  important enough to warrant its own mention. Again, saves code, makes stuff
  recognizable instantly and uses well-known Flask idioms. Also allows easily
  putting the API endpoints onto the app with any prefix.

In addition, it should be possible to easily implement the three levels of
REST- Apis. All the mentioned REST-extensions seem to go up only to level 2,
stopping short of Hypermedia Controls (HATEOAS); at the very least they are not
including them in examples. Another missing feature ("missing" not meaning
impossible-to- do, but not a first-class feature) seems to be *content-
negotiation*, especially if unconventional or vendor-specific content-types are
desired.
