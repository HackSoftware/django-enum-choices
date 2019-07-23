from django import forms

from django_enum_choices.forms import EnumChoiceField

from .models import MyModel
from .enumerations import MyEnum
from .choice_builders import custom_choice_builder


class StandardEnumForm(forms.Form):
    enumerated_field = EnumChoiceField(MyEnum)


class ModelEnumForm(forms.ModelForm):
    class Meta:
        model = MyModel
        fields = ['enumerated_field']


class CustomChoiceBuilderEnumForm(forms.Form):
    enumerated_field = EnumChoiceField(
        MyEnum,
        choice_builder=custom_choice_builder
    )
