from django.apps import apps
from django.db import models
from django.contrib.postgres import fields as pg_fields


POSTGRES = 'postgresql'
DEFAULT = 'default'


class DataBaseRouter:
    def _get_postgresql_fields(self):
        return [
            var for var in vars(pg_fields).values()
            if isinstance(var, type) and issubclass(var, models.Field)
        ]

    def _get_field_classes(self, db_obj):
        return [
            type(field) for field in db_obj._meta.get_fields()
        ]

    def has_postgres_field(self, db_obj):
        field_classes = self._get_field_classes(db_obj)

        return len([
            field_cls for field_cls in field_classes
            if field_cls in self._get_postgresql_fields()
        ]) > 0

    def db_for_read(self, model, **hints):
        if self.has_postgres_field(model):
            return POSTGRES

        return DEFAULT

    def db_for_write(self, model, **hints):
        if self.has_postgres_field(model):
            return POSTGRES

        return DEFAULT

    def allow_relation(self, obj1, obj2, **hints):
        if not self.has_postgres_field(obj1) and not self.has_postgres_field(obj2):
            return True

        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if model_name is not None and \
           db == DEFAULT and \
           self.has_postgres_field(apps.get_model(app_label, model_name)):
            return False

        return True
