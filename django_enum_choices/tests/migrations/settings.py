from __future__ import unicode_literals

import environ

from .database_routers import MultiDBrouter

env = environ.Env()

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:"
    },
    'postgresql': env.db('DATABASE_URL', default='postgres:///django_enum_choices'),
    'mysql': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'NAME': 'django_enum_choices',
        'USER': 'test_user',
        'PASSWORD': 'test_password',
        'OPTIONS': {
            'init_command': 'SET default_storage_engine=INNODB',
        }
    }
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
