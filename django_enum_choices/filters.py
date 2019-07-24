import django_filters as filters

from .fields import EnumChoiceField
from .forms import EnumChoiceField as EnumChoiceFormField
from .choice_builders import value_value


class EnumChoiceFilter(filters.ChoiceFilter):
    field_class = EnumChoiceFormField

    def __init__(self, enum_class, choice_builder=value_value, *args, **kwargs):
        super().__init__(
            enum_class=enum_class,
            choice_builder=choice_builder,
            *args,
            **kwargs
        )


class EnumChoiceFilterSetMixin:
    """
    `django-filter` has specific logic for handling fields with `choices`.
    We need to override `filter_for_lookup` to return an `EnumChoiceFilter`
    before `django-filter` returns a `ChoiceFilter` as the `filter_class`
    for the `EnumChoiceField` instances in the model.
    """

    @classmethod
    def filter_for_lookup(cls, field, lookup_type):
        if isinstance(field, EnumChoiceField):
            return EnumChoiceFilter, {
                'enum_class': field.enum_class,
                'choice_builder': field.choice_builder
            }

        return super().filter_for_lookup(field, lookup_type)
