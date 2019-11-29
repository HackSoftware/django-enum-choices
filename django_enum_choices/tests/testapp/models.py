from django.db import models
from django.contrib.postgres.fields import ArrayField

from django_enum_choices.fields import EnumChoiceField
from django_enum_choices.choice_builders import attribute_value

from .enumerations import CharTestEnum, CharLongValuesTestEnum, IntTestEnum


def custom_choice_builder(choice):
    return 'Custom_' + choice.value, choice.value


class IntegerEnumeratedModel(models.Model):
    enumeration = EnumChoiceField(enum_class=IntTestEnum)


class StringEnumeratedModel(models.Model):
    enumeration = EnumChoiceField(enum_class=CharTestEnum)


class NullableEnumeratedModel(models.Model):
    enumeration = EnumChoiceField(
        enum_class=CharTestEnum,
        null=True
    )


class BlankNullableEnumeratedModel(models.Model):
    enumeration = EnumChoiceField(
        enum_class=CharTestEnum,
        blank=True,
        null=True
    )


class EnumChoiceFieldWithDefaultModel(models.Model):
    enumeration = EnumChoiceField(
        CharTestEnum,
        default=CharTestEnum.FIRST
    )


class MultipleEnumeratedModel(models.Model):
    enumeration = ArrayField(
        base_field=EnumChoiceField(
            enum_class=CharTestEnum
        ),
        null=True
    )


class CustomChoiceBuilderEnumeratedModel(models.Model):
    enumeration = EnumChoiceField(
        enum_class=CharTestEnum,
        choice_builder=custom_choice_builder
    )


class AttributeChoiceBuilderEnumeratedModel(models.Model):
    enumeration = EnumChoiceField(
        enum_class=CharLongValuesTestEnum,
        choice_builder=attribute_value
    )
