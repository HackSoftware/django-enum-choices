from django.contrib import admin
from django.conf import settings

from .fields import EnumChoiceField


class EnumChoiceListFilter(admin.ChoicesFieldListFilter):
    def queryset(self, request, queryset):
        query = {
            field_name: self.field.to_enum_value(value)
            for field_name, value in self.used_parameters.items()
        }

        return queryset.filter(**query)


def register_enum_choice_list_filter():
    register_filter = getattr(
        settings,
        'DJANGO_ENUM_CHOICES_REGISTER_LIST_FILTER',
        False
    )

    if register_filter:
        admin.FieldListFilter.register(
            lambda f: isinstance(f, EnumChoiceField),
            EnumChoiceListFilter,
            take_priority=True
        )
