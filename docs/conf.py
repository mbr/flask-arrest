# -*- coding: utf-8 -*-

project = u'Flask-Arrest'
copyright = u'2016, Marc Brinkmann'
version = '0.5.0'
release = '0.5.0'

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.intersphinx',
              'sphinx.ext.graphviz', 'sphinx.ext.todo', 'alabaster']
source_suffix = '.rst'
master_doc = 'index'
exclude_patterns = ['_build']
pygments_style = 'monokai'

html_theme = 'alabaster'
html_theme_options = {
    'github_user': 'mbr',
    'github_repo': 'flask-arrest',
    'github_banner': True,
    'github_button': False,
    'show_powered_by': False,

    # required for monokai:
    'pre_bg': '#292429',
}
html_sidebars = {
    '**': [
        'about.html',
        'navigation.html',
        'relations.html',
        'searchbox.html',
        'donate.html',
    ]
}

intersphinx_mapping = {'http://docs.python.org/': None,
                       'http://flask-sqlalchemy.pocoo.org/': None,
                       'http://flask.pocoo.org/docs/': None,
                       'http://werkzeug.pocoo.org/docs/': None, }
