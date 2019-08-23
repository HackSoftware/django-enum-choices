from django.contrib import admin
from django.conf import settings
from django.utils.translation import gettext as _

from .fields import EnumChoiceField


class EnumChoiceListFilter(admin.ChoicesFieldListFilter):
    def choices(self, changelist):
        """
        The `choices` method from `django.contrib.admin.ChoicesFieldListFilter`
        with a patch to cast lookup values from enum enumerations to their respective
        primitive values.
        """

        yield {
            'selected': self.lookup_val is None,
            'query_string': changelist.get_query_string(
                remove=[
                    self.lookup_kwarg,
                    self.lookup_kwarg_isnull
                ]
            ),
            'display': _('All')
        }
        none_title = ''
        for lookup, title in self.field.flatchoices:
            lookup = self.field.get_prep_value(lookup)

            if lookup is None:
                none_title = title
                continue
            yield {
                'selected': str(lookup) == self.lookup_val,
                'query_string': changelist.get_query_string(
                    {self.lookup_kwarg: lookup},
                    [self.lookup_kwarg_isnull]
                ),
                'display': title,
            }
        if none_title:
            yield {
                'selected': bool(self.lookup_val_isnull),
                'query_string': changelist.get_query_string(
                    {self.lookup_kwarg_isnull: 'True'},
                    [self.lookup_kwarg]
                ),
                'display': none_title,
            }

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
