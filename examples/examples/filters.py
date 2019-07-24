import django_filters as filters

from django_enum_choices.filters import EnumChoiceFilter, EnumChoiceFilterSetMixin

from .enumerations import MyEnum
from .models import MyModel
from .choice_builders import custom_choice_builder


class ExplicitFilterSet(filters.FilterSet):
    enumerated_field = EnumChoiceFilter(MyEnum)


class ExplicitCustomChoiceBuilderFilterSet(filters.FilterSet):
    enumerated_field = EnumChoiceFilter(
        MyEnum,
        choice_builder=custom_choice_builder
    )


class ImplicitFilterSet(EnumChoiceFilterSetMixin, filters.FilterSet):
    class Meta:
        model = MyModel
        fields = ['enumerated_field']
