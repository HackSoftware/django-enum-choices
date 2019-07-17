def as_choice_builder(func):
    def inner(enumeration):
        if not enumeration:
            return enumeration

        built = func(enumeration)

        return tuple(str(value) for value in built)

    return inner


def value_value(enumeration):
    return (
        enumeration.value,
        enumeration.value
    )


def attribute_attribute(enumeration):
    return (
        enumeration.name,
        enumeration.name
    )


def attribute_value(enumeration):
    return (
        enumeration.name,
        enumeration.value
    )


def value_attribute(enumeration):
    return (
        enumeration.value,
        enumeration.name
    )
