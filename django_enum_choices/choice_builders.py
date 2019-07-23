from enum import Enum
from typing import Tuple


def value_value(enumeration: Enum) -> Tuple[str, str]:
    return (
        str(enumeration.value),
        str(enumeration.value)
    )


def attribute_attribute(enumeration: Enum) -> Tuple[str, str]:
    return (
        str(enumeration.name),
        str(enumeration.name)
    )


def attribute_value(enumeration: Enum) -> Tuple[str, str]:
    return (
        str(enumeration.name),
        str(enumeration.value)
    )


def value_attribute(enumeration: Enum) -> Tuple[str, str]:
    return (
        str(enumeration.value),
        str(enumeration.name)
    )
