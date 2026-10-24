"""
Django settings module that imports from settings_dev.py.

This file exists because manage.py and wsgi.py reference 'recipy.settings',
but the actual settings are in settings_dev.py.
"""

from recipy.settings_dev import *  # noqa: F401, F403
