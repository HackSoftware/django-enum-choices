from django.core.validators import MaxLengthValidator


class EnumValueMaxLengthValidator(MaxLengthValidator):
    """
    When called from the field's `run_validators`, `MaxLengthValidator`
    attempts to return `len(value)` when value is an enumeration
    instance, which raises an error
    """
    def __init__(self, validate_attribute_name: bool = False, *args, **kwargs):
        self.validate_attribute_name = validate_attribute_name

        super().__init__(*args, **kwargs)

    def clean(self, x):
        value_to_validate = x.name if self.validate_attribute_name else x.value
        return len(str(value_to_validate))
