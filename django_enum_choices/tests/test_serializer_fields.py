from django.test import TestCase

from rest_framework.exceptions import ValidationError

from django_enum_choices.serializers import EnumChoiceField, MultipleEnumChoiceField
from .testapp.enumerations import IntTestEnum, CharTestEnum


class TestSerializerField(TestCase):
    def test_to_representation_returns_primitive_int_value(self):
        field = EnumChoiceField(enum_class=IntTestEnum)

        result = field.to_representation(IntTestEnum.FIRST)

        self.assertEqual(result, 1)

    def test_to_representation_returns_primitive_string_value(self):
        field = EnumChoiceField(enum_class=CharTestEnum)

        result = field.to_representation(CharTestEnum.FIRST)

        self.assertEqual(result, 'first')

    def test_to_internal_value_fails_when_value_not_in_enum_class(self):
        failing_value = 5
        field = EnumChoiceField(enum_class=IntTestEnum)

        with self.assertRaisesMessage(
            ValidationError,
            'Key 5 is not a valid IntTestEnum'
        ):
            field.to_internal_value(failing_value)

    def test_to_internal_value_returns_enum_value_when_value_is_int(self):
        field = EnumChoiceField(enum_class=IntTestEnum)

        result = field.to_internal_value(1)

        self.assertEqual(result, IntTestEnum.FIRST)

    def test_to_internal_value_returns_enum_value_when_value_is_string(self):
        field = EnumChoiceField(enum_class=CharTestEnum)

        result = field.to_internal_value('first')

        self.assertEqual(result, CharTestEnum.FIRST)


class TestMultipleSerializerField(TestCase):
    def test_to_representation_returns_list_of_ints(self):
        field = MultipleEnumChoiceField(enum_class=IntTestEnum)

        result = field.to_representation([IntTestEnum.FIRST, IntTestEnum.SECOND])

        self.assertEqual([1, 2], result)

    def test_to_representation_returns_list_of_strings(self):
        field = MultipleEnumChoiceField(enum_class=CharTestEnum)

        result = field.to_representation([CharTestEnum.FIRST, CharTestEnum.SECOND])

        self.assertEqual(['first', 'second'], result)

    def test_to_internal_value_fails_when_value_is_not_list(self):
        field = MultipleEnumChoiceField(enum_class=IntTestEnum)

        with self.assertRaisesMessage(
            ValidationError,
            'Expected a list of items but got type "int".'
        ):
            field.to_internal_value(5)

    def test_to_internal_value_fails_when_not_allowed_empty_field_gets_empty_list(self):
        field = MultipleEnumChoiceField(enum_class=IntTestEnum)

        with self.assertRaisesMessage(
            ValidationError,
            'This selection may not be empty.'
        ):
            field.to_internal_value([])

    def test_to_internal_value_returns_list_of_enums_when_value_is_list_of_ints(self):
        field = MultipleEnumChoiceField(enum_class=IntTestEnum)

        result = field.to_internal_value([1, 2])

        self.assertEqual([IntTestEnum.FIRST, IntTestEnum.SECOND], result)

    def test_to_internal_value_returns_list_of_enums_when_value_is_list_of_strings(self):
        field = MultipleEnumChoiceField(enum_class=CharTestEnum)

        result = field.to_internal_value(['first', 'second'])

        self.assertEqual([CharTestEnum.FIRST, CharTestEnum.SECOND], result)
