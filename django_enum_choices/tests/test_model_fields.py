from enum import Enum

from django.test import TestCase
from django.core.exceptions import ValidationError

from django_enum_choices.fields import EnumChoiceField
from django_enum_choices.exceptions import EnumChoiceFieldException

from .testapp.enumerations import CharTestEnum, IntTestEnum


class EnumChoiceFieldTests(TestCase):
    def test_field_initializes_string_choice_values(self):
        field = EnumChoiceField(enum_class=CharTestEnum)

        self.assertEqual(
            field.enum_class,
            CharTestEnum
        )

        expected_choices = [
            ('first', 'first'),
            ('second', 'second'),
            ('third', 'third'),
        ]

        self.assertEqual(
            expected_choices,
            field.choices,
        )

    def test_field_initializes_int_choice_values_by_stringifying_them(self):
        field = EnumChoiceField(enum_class=IntTestEnum)

        self.assertEqual(
            field.enum_class,
            IntTestEnum
        )

        expected_choices = [
            ('1', '1'),
            ('2', '2'),
            ('3', '3'),
        ]

        self.assertEqual(
            expected_choices,
            field.choices,
        )

    def test_field_initializes_arbitrary_object_values_by_stringifying_them(self):
        class Foo:
            def __str__(self):
                return 'foo'

        class TestEnum(Enum):
            FOO = Foo()

        field = EnumChoiceField(enum_class=TestEnum)

        expected_choices = [
            ('foo', 'foo')
        ]

        self.assertEqual(
            expected_choices,
            field.choices,
        )

    def test_max_length_is_calculated_from_the_longest_element(self):

        class TestEnum(Enum):
            FOO = 'foo'
            BAR = 'A' * 100

        field = EnumChoiceField(enum_class=TestEnum)

        self.assertEqual(100, field.max_length)

    def test_field_raises_exception_when_enum_class_is_not_enumeration(self):
        class FailingEnum:
            FOO = 'foo'
            BAR = 'bar'

        with self.assertRaisesMessage(
            EnumChoiceFieldException,
            '`enum_class` argument must be a child of `Enum`'
        ):
            EnumChoiceField(enum_class=FailingEnum)

    def test_get_prep_value_returns_primitive_value_when_base_is_integer(self):
        instance = EnumChoiceField(enum_class=IntTestEnum)

        result = instance.get_prep_value(IntTestEnum.FIRST)

        self.assertEqual(result, '1')

    def test_get_prep_value_returns_primitive_value_when_base_is_string(self):
        instance = EnumChoiceField(enum_class=CharTestEnum)

        result = instance.get_prep_value(CharTestEnum.FIRST)

        self.assertEqual(result, 'first')

    def test_from_db_value_returns_none_when_value_is_none(self):
        instance = EnumChoiceField(enum_class=IntTestEnum)

        result = instance.from_db_value(None, None, None)

        self.assertIsNone(result)

    def test_from_db_value_returns_enum_value_when_base_is_integer(self):
        instance = EnumChoiceField(enum_class=IntTestEnum)

        result = instance.from_db_value('1', None, None)

        self.assertEqual(result, IntTestEnum.FIRST)

    def test_from_db_value_returns_enum_value_when_base_is_string(self):
        instance = EnumChoiceField(enum_class=CharTestEnum)

        result = instance.from_db_value('first', None, None)

        self.assertEqual(result, CharTestEnum.FIRST)

    def test_from_db_value_raises_exception_when_int_value_not_contained_in_enum_class(self):
        instance = EnumChoiceField(enum_class=IntTestEnum)

        with self.assertRaises(ValidationError):
            instance.from_db_value(7, None, None)

    def test_deconstruct_behaves_as_expected(self):
        """
        Idea taken from:
        https://docs.djangoproject.com/en/2.2/howto/custom-model-fields/#field-deconstruction
        """
        instance = EnumChoiceField(enum_class=IntTestEnum)
        name, path, args, kwargs = instance.deconstruct()

        new_instance = EnumChoiceField(*args, **kwargs)

        self.assertEqual(instance.enum_class, new_instance.enum_class)
        self.assertEqual(instance.choices, new_instance.choices)
        self.assertEqual(instance.max_length, new_instance.max_length)

    def test_get_readable_should_be_a_callable(self):
        class TestEnum(Enum):
            A = 1
            B = 2

            get_readable_value = 3
        instance = EnumChoiceField(enum_class=TestEnum)

        expected_choices = [
            ('1', '1'),
            ('2', '2'),
            ('3', '3')
        ]

        self.assertEqual(expected_choices, instance.choices)

    def test_get_readable_value_is_used_when_callable(self):
        class TestEnum(Enum):
            A = 1
            B = 2

            def get_readable_value(enum_instance):
                if enum_instance == TestEnum.A:
                    return 'A'

                if enum_instance == TestEnum.B:
                    return 'B'

        instance = EnumChoiceField(enum_class=TestEnum)

        expected_choices = [
            ('1', 'A'),
            ('2', 'B')
        ]

        self.assertEqual(expected_choices, instance.choices)

    def test_to_python_returns_enum_when_called_with_enum_value(self):
        instance = EnumChoiceField(enum_class=CharTestEnum)

        result = instance.to_python(CharTestEnum.FIRST)

        self.assertEqual(CharTestEnum.FIRST, result)

    def test_to_python_returns_enum_when_called_with_primitive_value(self):
        instance = EnumChoiceField(enum_class=CharTestEnum)

        result = instance.to_python('first')

        self.assertEqual(CharTestEnum.FIRST, result)

    def test_to_python_returns_none_when_called_with_none(self):
        instance = EnumChoiceField(enum_class=CharTestEnum)

        result = instance.to_python(None)

        self.assertIsNone(result)

    def test_to_python_raises_exception_when_called_with_value_outside_enum_class(self):
        instance = EnumChoiceField(enum_class=CharTestEnum)

        with self.assertRaises(
            ValidationError
        ):
            instance.to_python('NOT_EXISTING')
