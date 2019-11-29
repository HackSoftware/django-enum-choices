from typing import Callable

from django.core.validators import MaxLengthValidator


class EnumValueMaxLengthValidator(MaxLengthValidator):
    """
    When called from the field's `run_validators`, `MaxLengthValidator`
    attempts to return `len(value)` when value is an enumeration
    instance, which raises an error
    """
    def __init__(self, value_builder: Callable,  *args, **kwargs):
        self.value_builder = value_builder

        super().__init__(*args, **kwargs)

    def clean(self, x):
        value = self.value_builder(x)

        return len(value)
