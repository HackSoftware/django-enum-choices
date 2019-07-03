from __future__ import unicode_literals

import environ

env = environ.Env()

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:"
    },
    'postgresql': env.db('DATABASE_URL', default='postgres:///django_enum_choices')

}

DATABASE_ROUTERS = ['tests.testapp.database_routers.DataBaseRouter']

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "tests.testapp.apps.TestAppConfig"
]

SITE_ID = 1

SECRET_KEY = "test"
