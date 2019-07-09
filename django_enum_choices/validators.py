from django.core.validators import MaxLengthValidator


class EnumValueMaxLengthValidator(MaxLengthValidator):
    """
    When called from the field's `run_validators`, `MaxLengthValidator`
    attempts to return `len(value)` when value is an enumeration
    instance, which raises an error
    """

    def clean(self, x):
        return len(x.value)
