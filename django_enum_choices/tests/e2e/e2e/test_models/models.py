from enum import Enum

from django.db import models

from django_enum_choices.fields import EnumChoiceField


class Choices(Enum):
    A = 'a'
    B = 'aa'
    C = 'aaa'
    # D = 'aaaa'


class SomeModel(models.Model):
    choices = EnumChoiceField(Choices)
