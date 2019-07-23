from typing import Callable, Tuple
from enum import Enum
from itertools import chain

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


def build_enum_choices(
    enum_class: Enum,
    choice_builder: Callable
) -> Tuple[Tuple[str]]:
    choices = [
        choice_builder(choice)
        for choice in enum_class
    ]

    if not all(
        isinstance(value, str) for value
        in chain.from_iterable(choices)
    ):
        raise EnumChoiceFieldException(
            _('All choices generated from {} must be strings.'.format(
                enum_class.__name__
            ))
        )

    return choices
