from enum import Enum

from django.db import models

from django_enum_choices.fields import EnumChoiceField


class ChoicesA(Enum):
    A = 'a'
    B = 'aa'
    C = 'aaa'
    #TEST_1 D = 'aaaa'


class ChoicesB(Enum):
    A = 'a'
    #TEST_2 B = 'b'


class SomeModel(models.Model):
    choices = EnumChoiceField(ChoicesA)

    other_choices = EnumChoiceField(ChoicesB)
