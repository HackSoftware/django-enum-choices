from django.test import TestCase

import django_filters as filters
from django_filters import rest_framework as drf_filters

from django_enum_choices.filters import EnumChoiceFilter, EnumChoiceFilterSetMixin

from .testapp.enumerations import CharTestEnum
from .testapp.models import (
    StringEnumeratedModel,
    CustomChoiceBuilderEnumeratedModel,
    custom_choice_builder
)


class FilterSetIntegrationTests(TestCase):
    class ExplicitFilterSet(filters.FilterSet):
        enumeration = EnumChoiceFilter(CharTestEnum)

    class ExplicitChoiceBuilderFilterSet(filters.FilterSet):
        enumeration = EnumChoiceFilter(CharTestEnum, choice_builder=custom_choice_builder)

    class ImplicitFilterSet(EnumChoiceFilterSetMixin, filters.FilterSet):
        class Meta:
            model = StringEnumeratedModel
            fields = ['enumeration']

    class ImplicitChoiceBuilderFilterSet(EnumChoiceFilterSetMixin, filters.FilterSet):
        class Meta:
            model = CustomChoiceBuilderEnumeratedModel
            fields = ['enumeration']

    def setUp(self):
        for choice in CharTestEnum:
            StringEnumeratedModel.objects.create(
                enumeration=choice
            )

    def test_explicitly_declarated_field_filters_correctly(self):
        filters = {
            'enumeration': 'first'
        }
        filterset = self.ExplicitFilterSet(filters, StringEnumeratedModel.objects.all())

        self.assertEqual(filterset.qs.count(), 1)
        self.assertEqual(filterset.qs.first().enumeration, CharTestEnum.FIRST)

    def test_explicitly_declarated_field_filters_correctly_with_custom_choice_builder(self):
        filters = {
            'enumeration': 'Custom_first'
        }
        filterset = self.ExplicitChoiceBuilderFilterSet(filters, StringEnumeratedModel.objects.all())

        self.assertEqual(filterset.qs.count(), 1)
        self.assertEqual(filterset.qs.first().enumeration, CharTestEnum.FIRST)

    def test_filter_by_non_valid_choice_returns_full_queryset(self):
        filters = {
            'enumeration': 'invalid'
        }
        filterset = self.ExplicitChoiceBuilderFilterSet(filters, StringEnumeratedModel.objects.all())

        self.assertEqual(filterset.qs.count(), StringEnumeratedModel.objects.count())

    def test_implicit_filter_filters_correctly(self):
        filters = {
            'enumeration': 'first'
        }
        filterset = self.ImplicitFilterSet(filters)

        self.assertEqual(filterset.qs.count(), 1)
        self.assertEqual(filterset.qs.first().enumeration, CharTestEnum.FIRST)

    def test_implicit_filter_filters_correctly_on_field_with_custom_choice_builder(self):
        for choice in CharTestEnum:
            CustomChoiceBuilderEnumeratedModel.objects.create(enumeration=choice)

        filters = {
            'enumeration': 'Custom_first'
        }
        filterset = self.ImplicitChoiceBuilderFilterSet(filters)

        self.assertEqual(filterset.qs.count(), 1)
        self.assertEqual(filterset.qs.first().enumeration, CharTestEnum.FIRST)


class FilterSetDRFIntegrationTests(TestCase):
    class ExplicitFilterSet(drf_filters.FilterSet):
        enumeration = EnumChoiceFilter(CharTestEnum)

    class ExplicitChoiceBuilderFilterSet(drf_filters.FilterSet):
        enumeration = EnumChoiceFilter(CharTestEnum, choice_builder=custom_choice_builder)

    class ImplicitFilterSet(EnumChoiceFilterSetMixin, drf_filters.FilterSet):
        class Meta:
            model = StringEnumeratedModel
            fields = ['enumeration']

    class ImplicitChoiceBuilderFilterSet(EnumChoiceFilterSetMixin, drf_filters.FilterSet):
        class Meta:
            model = CustomChoiceBuilderEnumeratedModel
            fields = ['enumeration']

    def setUp(self):
        for choice in CharTestEnum:
            StringEnumeratedModel.objects.create(
                enumeration=choice
            )

    def test_explicitly_declarated_field_filters_correctly(self):
        filters = {
            'enumeration': 'first'
        }
        filterset = self.ExplicitFilterSet(filters, StringEnumeratedModel.objects.all())

        self.assertEqual(filterset.qs.count(), 1)
        self.assertEqual(filterset.qs.first().enumeration, CharTestEnum.FIRST)

    def test_explicitly_declarated_field_filters_correctly_with_custom_choice_builder(self):
        filters = {
            'enumeration': 'Custom_first'
        }
        filterset = self.ExplicitChoiceBuilderFilterSet(filters, StringEnumeratedModel.objects.all())

        self.assertEqual(filterset.qs.count(), 1)
        self.assertEqual(filterset.qs.first().enumeration, CharTestEnum.FIRST)

    def test_filter_by_non_valid_choice_returns_full_queryset(self):
        filters = {
            'enumeration': 'invalid'
        }
        filterset = self.ExplicitChoiceBuilderFilterSet(filters, StringEnumeratedModel.objects.all())

        self.assertEqual(filterset.qs.count(), StringEnumeratedModel.objects.count())

    def test_implicit_filter_filters_correctly(self):
        filters = {
            'enumeration': 'first'
        }
        filterset = self.ImplicitFilterSet(filters)

        self.assertEqual(filterset.qs.count(), 1)
        self.assertEqual(filterset.qs.first().enumeration, CharTestEnum.FIRST)

    def test_implicit_filter_filters_correctly_on_field_with_custom_choice_builder(self):
        for choice in CharTestEnum:
            CustomChoiceBuilderEnumeratedModel.objects.create(enumeration=choice)

        filters = {
            'enumeration': 'Custom_first'
        }
        filterset = self.ImplicitChoiceBuilderFilterSet(filters)

        self.assertEqual(filterset.qs.count(), 1)
        self.assertEqual(filterset.qs.first().enumeration, CharTestEnum.FIRST)
