from django.db import models
from django.contrib.postgres.fields import ArrayField

from django_enum_choices.fields import EnumChoiceField

from .enumerations import MyEnum


# Model, containing a field with enumerations as choices
class MyModel(models.Model):
    enumerated_field = EnumChoiceField(MyEnum)


# Model, containing a field with a array of enumerations (PostgreSQL specific)
class MyModelMultiple(models.Model):
    enumerated_field = ArrayField(
        base_field=EnumChoiceField(MyEnum)
    )


def choice_builder(choice):
    return choice.value, choice.value.upper()


class CustomReadableValueEnumModel(models.Model):
    enumerated_field = EnumChoiceField(
        MyEnum,
        choice_builder=choice_builder
    )
