from enum import Enum
from typing import Tuple, Any


def value_value(enumeration: Enum) -> Tuple[Any, Any]:
    return (
        enumeration.value,
        enumeration.value
    )


def attribute_attribute(enumeration: Enum) -> Tuple[str, str]:
    return (
        enumeration.name,
        enumeration.name
    )


def attribute_value(enumeration: Enum) -> Tuple[str, Any]:
    return (
        enumeration.name,
        enumeration.value
    )


def value_attribute(enumeration: Enum) -> Tuple[Any, str]:
    return (
        enumeration.value,
        enumeration.name
    )
