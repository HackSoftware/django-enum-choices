from django.test import TestCase, RequestFactory, override_settings
from django.contrib import admin
from django.contrib.auth.models import User

from django_enum_choices.admin import EnumChoiceListFilter, register_enum_choice_list_filter

from .testapp.models import StringEnumeratedModel
from .testapp.enumerations import CharTestEnum


class StringEnumAdmin(admin.ModelAdmin):
    list_filter = ('enumeration', )


class EnumChoiceListFilterTests(TestCase):
    request_factory = RequestFactory()

    def setUp(self):
        self.user = User.objects.create_superuser('user', 'user@example.com', 'password')

    # Django 1.11 compatibillity
    def get_changelist_instance(self, request, model, modeladmin):
        changelist_args = [
            request, model, modeladmin.list_display,
            modeladmin.list_display_links, modeladmin.list_filter,
            modeladmin.date_hierarchy, modeladmin.search_fields,
            modeladmin.list_select_related, modeladmin.list_per_page,
            modeladmin.list_max_show_all, modeladmin.list_editable, modeladmin,
        ]

        try:
            changelist = modeladmin.get_changelist(request)(*changelist_args)
        except TypeError:
            # Django < 2 does not accept `sortable_by` in `ChangeList`
            changelist_args.append(modeladmin.sortable_by)
            changelist = modeladmin.get_changelist(request)(*changelist_args)

        return changelist

    @override_settings(DJANGO_ENUM_CHOICES_REGISTER_LIST_FILTER=True)
    def test_list_filter_instance_is_enumchoicelistfilter_when_registered(self):
        register_enum_choice_list_filter()

        modeladmin = StringEnumAdmin(
            StringEnumeratedModel,
            admin.site
        )
        request = self.request_factory.get('/', {})
        request.user = self.user

        changelist = self.get_changelist_instance(request, StringEnumeratedModel, modeladmin)
        filterspec = changelist.get_filters(request)[0][0]

        self.assertIsInstance(filterspec, EnumChoiceListFilter)

    @override_settings(DJANGO_ENUM_CHOICES_REGISTER_LIST_FILTER=True)
    def test_list_filter_lookup_kwarg_is_correct(self):
        register_enum_choice_list_filter()

        modeladmin = StringEnumAdmin(
            StringEnumeratedModel,
            admin.site
        )
        request = self.request_factory.get('/', {})
        request.user = self.user

        changelist = self.get_changelist_instance(request, StringEnumeratedModel, modeladmin)
        filterspec = changelist.get_filters(request)[0][0]

        self.assertEqual(filterspec.lookup_kwarg, 'enumeration__exact')

    @override_settings(DJANGO_ENUM_CHOICES_REGISTER_LIST_FILTER=True)
    def test_list_filter_queryset_filters_objects_correctly(self):
        StringEnumeratedModel.objects.create(enumeration=CharTestEnum.FIRST)
        StringEnumeratedModel.objects.create(enumeration=CharTestEnum.SECOND)
        StringEnumeratedModel.objects.create(enumeration=CharTestEnum.THIRD)

        modeladmin = StringEnumAdmin(
            StringEnumeratedModel,
            admin.site
        )

        for enumeration in CharTestEnum:
            request = self.request_factory.get('/', {'enumeration__exact': enumeration.value})
            request.user = self.user

            changelist = self.get_changelist_instance(request, StringEnumeratedModel, modeladmin)

            self.assertEqual(changelist.queryset.count(), 1)
