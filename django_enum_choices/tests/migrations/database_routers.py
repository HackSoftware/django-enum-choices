from django.conf import settings


class MultiDBrouter:
    def db_for_read(self, model, **hints):
        return settings.CURRENT_DATABASE

    def db_for_write(self, model, **hints):
        return settings.CURRENT_DATABASE

    def allow_relation(self, obj1, obj2, **hints):
        return settings.CURRENT_DATABASE

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return settings.CURRENT_DATABASE
