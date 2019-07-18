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
