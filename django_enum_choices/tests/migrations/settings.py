from __future__ import unicode_literals

import environ

from .database_routers import MultiDBrouter

env = environ.Env()

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:"
    },
    'postgresql': env.db('DATABASE_URL', default='postgres:///django_enum_choices')
}

DATABASE_ROUTERS = [MultiDBrouter()]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "tests.migrations.migrations_testapp.apps.MigrationsTestAppConfig"
]

# Used alongside `MutliDBRouter` to define which database is used inside the tests
CURRENT_DATABASE = 'default'

SITE_ID = 1

SECRET_KEY = "test"
