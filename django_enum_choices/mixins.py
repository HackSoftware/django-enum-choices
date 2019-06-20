from enum import Enum

from .exceptions import EnumChoiceFieldException


class EnumInternalFieldMixin:
    def __init__(self, enum_class: Enum, *args, **kwargs):
        self.enum_class = enum_class

        super().__init__(*args, **kwargs)

    def to_enum_value(self, value):
        if value is None:
            return

        try:
            return self.enum_class(value)
        except ValueError as exc:
            raise EnumChoiceFieldException(str(exc))

    def to_db_value(self, value):
        if value is None:
            return

        return value.value

    def get_prep_value(self, value):
        return self.to_db_value(value)

    def from_db_value(self, value, expression, connection):
        return self.to_enum_value(value)

    def to_python(self, value):
        if isinstance(value, self.enum_class):
            return value

        return self.to_enum_value(value)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()

        if self.enum_class:
            kwargs['enum_class'] = self.enum_class

        return name, path, args, kwargs
