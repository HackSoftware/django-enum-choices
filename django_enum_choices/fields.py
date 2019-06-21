from enum import Enum
from typing import Tuple, Union

from django.db.models import CharField

from .exceptions import EnumChoiceFieldException


class EnumChoiceField(CharField):
    def __init__(self, enum_class: Enum, **kwargs):
        if not (Enum in enum_class.__mro__):
            raise EnumChoiceFieldException(
                '`enum_class` argument must be a child of `Enum`'
            )

        self.enum_class = enum_class

        kwargs['choices'] = self.build_choices()
        kwargs['max_length'] = self._calculate_max_length(**kwargs)

        super().__init__(**kwargs)

    def _pack_choices(self) -> Tuple[Tuple[Union[int, str]]]:
        return [(str(choice.value), str(choice.value)) for choice in self.enum_class]

    def build_choices(self):
        packed_choices = self._pack_choices()

        if hasattr(self.enum_class, 'get_readable_value'):
            # Used if different readable values are wanted from the
            # ones stored in the enum class
            packed_choices = [(
                str(choice.value), self.enum_class.get_readable_value(choice)
            ) for choice in self.enum_class]

        return packed_choices

    def _calculate_max_length(self, **kwargs) -> int:
        max_length = kwargs.get('max_length')

        if max_length is None:
            max_length = max([len(choice) for choice, _ in kwargs['choices']])

        if max_length < 255:
            max_length = 255

        return max_length

    def to_enum_value(self, value):
        if value is None:
            return

        for choice in self.enum_class:
            if str(choice.value) == value:
                return choice

        raise EnumChoiceFieldException(
            f'Value {value} not found in {self.enum_class}'
        )

    def to_db_value(self, value):
        if value is None:
            return

        return str(value.value)

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
