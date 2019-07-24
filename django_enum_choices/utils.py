from typing import Callable, Tuple, Any
from enum import Enum

from django.utils.translation import gettext as _

from .exceptions import EnumChoiceFieldException


def as_choice_builder(choice_builder):
    def inner(enumeration):
        if not enumeration:
            return enumeration

        built = choice_builder(enumeration)

        return tuple(str(value) for value in built)

    return inner


def value_from_built_choice(built_choice):
    if isinstance(built_choice, tuple):
        return built_choice[0]

    return built_choice


def validate_built_choices(
    enum_class: Enum,
    built_choices: Tuple[Tuple[Any]]
):
    MEMBER_KEY = 'key'
    MEMBER_VALUE = 'value'

    message = _(
        'Received type {failing_type} on {failing_member} inside choice: {failing_choice}.\n' +
        'All choices generated from {failing_enum_class} must be strings.'
    )

    for key, value in built_choices:
        message_kwargs = {
            'failing_choice': (key, value),
            'failing_enum_class': enum_class
        }

        if not isinstance(key, str):
            message_kwargs.update({
                'failing_type': type(key),
                'failing_member': MEMBER_KEY
            })

            raise EnumChoiceFieldException(
                message.format(**message_kwargs)
            )

        if not isinstance(value, str):
            message_kwargs.update({
                'failing_type': type(value),
                'failing_member': MEMBER_VALUE
            })

            raise EnumChoiceFieldException(
                message.format(**message_kwargs)
            )


def build_enum_choices(
    enum_class: Enum,
    choice_builder: Callable
) -> Tuple[Tuple[str]]:
    choices = [
        choice_builder(choice)
        for choice in enum_class
    ]

    validate_built_choices(enum_class, choices)

    return choices
