from enum import Enum
from typing import Tuple, Union

from django.db.models import IntegerField, CharField

from .mixins import EnumInternalFieldMixin
from .exceptions import EnumChoiceFieldException


class EnumIntegerField(EnumInternalFieldMixin, IntegerField):
    # TODO: Implement `deconstruct`

    def __init__(self, enum_class, *args, **kwargs):
        super().__init__(enum_class, *args, **kwargs)


class EnumCharField(EnumInternalFieldMixin, CharField):
    def __init__(self, enum_class, *args, **kwargs):
        super().__init__(enum_class, *args, **kwargs)


class EnumChoiceField:
    def __new__(cls, enum_class: Enum, **kwargs):
        if not (Enum in enum_class.__mro__):
            raise EnumChoiceFieldException(
                '`enum_class` argument must be a child of `Enum`'
            )

        instance = EnumChoiceFieldBuilder(enum_class, **kwargs)

        base = instance.get_inferred_base()

        return instance.get_swapped_instance(base, **kwargs)


class EnumChoiceFieldBuilder:
    # TODO: Support custom bases

    def __init__(self, enum_class: Enum, **kwargs):
        self.enum_class = enum_class
        self._choices = [choice.value for choice in enum_class]

    def _pack_choices(self) -> Tuple[Tuple[Union[int, str]]]:
        return ((choice, choice) for choice in self._choices)

    def get_inferred_base(self):
        field_mapping = {
            str: EnumCharField,
            int: EnumIntegerField
        }

        value_types = set(type(value) for value in self._choices)

        if value_types:
            if len(value_types) > 1:
                raise EnumChoiceFieldException(
                    'All choices in provided enum class must be of the same type' # noqa
                )

            return field_mapping.get(list(value_types)[0])

    def get_swapped_instance(self, base, **kwargs):
        packed_choices = self._pack_choices()

        if hasattr(self.enum_class, 'get_choices'):
            # Used if different readable values are wanted from the
            # ones stored in the enum class
            packed_choices = self.enum_class.get_choices()

        if base is EnumIntegerField:
            return base(
                enum_class=self.enum_class,
                choices=packed_choices,
                **kwargs
            )

        if base is EnumCharField:
            max_length = self._calculate_max_length(**kwargs)

            # Removing `max_length` as it is calculated explicitly.
            kwargs.pop('max_length', None)

            return base(
                enum_class=self.enum_class,
                choices=packed_choices,
                max_length=max_length,
                **kwargs
            )

    def _calculate_max_length(self, **kwargs) -> int:
        max_length = kwargs.get('max_length')

        if max_length is None:
            max_length = max([len(choice) for choice in self._choices])

        if max_length < 255:
            max_length = 255

        return max_length
