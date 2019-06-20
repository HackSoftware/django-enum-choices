from rest_framework import serializers


class EnumChoiceField(serializers.Field):
    # TODO: `many` behaviour; `ModelSerializer` implicit conversion

    NO_KEY_MSG = 'Key {failing_key} is not a valid {enum_class_name}'

    default_error_messages = {
        'non_existent_key': NO_KEY_MSG
    }

    def __init__(self, enum_class, **kwargs):
        super().__init__(**kwargs)
        self.enum_class = enum_class

    def to_representation(self, value):
        return value.value

    def to_internal_value(self, value):
        # TODO: Handle extra arguments: `allow_null`, `required`, etc

        try:
            return self.enum_class(value)
        except ValueError:
            self.fail(
                'non_existent_key',
                failing_key=value,
                enum_class_name=self.enum_class.__name__
            )
