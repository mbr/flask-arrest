#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='Flask-arrest',
    version='0.4.5.dev1',
    description='A small Flask extension to ease the creation of REST apis.',
    long_description=read('README.rst'),
    author='Marc Brinkmann',
    author_email='git@marcbrinkmann.de',
    url='http://github.com/mbr/Flask-arrest',
    license='MIT',
    packages=find_packages(exclude=['test']),
    install_requires=['Flask', 'werkzeug', 'jsonext'],
    tests_require=['pytest'],
)
