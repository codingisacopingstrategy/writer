#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
# Where to write the static files
PUBLIC_PATH = PUBLISH_DIR = os.path.join(PROJECT_DIR, '..', '..', 'I-like-tight-pants-and-mathematics')

# Additional locations of static files
STATICFILES_DIRS = (
    PUBLIC_PATH,
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

USE_TZ = True

# Through the fabfile.py we can launch actions on an external install
FABRIC_HOSTS = ['foo@bar.be']
FABRIC_PATH = '/the/path/to/external/public/path'
FABRIC_DJANGO_PATH = '/where/do/we/find/this/repo/external/'
