from __future__ import unicode_literals

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:"
    },
    'postgresql': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'django_enum_choices'
    }
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
