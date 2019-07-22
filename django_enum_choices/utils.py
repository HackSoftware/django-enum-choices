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
