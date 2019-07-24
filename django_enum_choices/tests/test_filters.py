from django.test import TestCase

from django_enum_choices.filters import EnumChoiceFilter
from django_enum_choices.forms import EnumChoiceField as EnumChoiceFormField

from .testapp.enumerations import CharTestEnum


class EnumChoiceFilterTests(TestCase):
    def test_filter_instance_extra_has_enum_class_and_choice_builder(self):
        instance = EnumChoiceFilter(enum_class=CharTestEnum)

        self.assertEqual(instance.extra['enum_class'], CharTestEnum)
        self.assertIsNotNone(instance.extra['choice_builder'])

    def test_corresponding_field_is_of_correct_type(self):
        instance = EnumChoiceFilter(enum_class=CharTestEnum)
        form_field = instance.field

        self.assertIsInstance(form_field, EnumChoiceFormField)

    def test_corresponding_field_has_enum_class_and_choice_builder(self):
        instance = EnumChoiceFilter(enum_class=CharTestEnum)

        form_field = instance.field

        self.assertEqual(form_field.enum_class, CharTestEnum)
        self.assertIsNotNone(form_field.choice_builder)
