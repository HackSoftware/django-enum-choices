from django.core.validators import MaxLengthValidator


class EnumValueMaxLengthValidator(MaxLengthValidator):
    def clean(self, x):
        return len(x.value)
