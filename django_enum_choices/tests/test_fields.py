from enum import Enum

from django.test import TestCase
from django.core import serializers
from django.core.exceptions import ValidationError

from django_enum_choices.fields import EnumChoiceField
from django_enum_choices.exceptions import EnumChoiceFieldException
from .testapp.enumerations import CharTestEnum, IntTestEnum
from .testapp.models import (
    IntegerEnumeratedModel,
    StringEnumeratedModel,
    NullableEnumeratedModel,
    BlankNullableEnumeratedModel
)


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

    def test_builder_initializes_int_choice_values(self):
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

    def test_builder_initializes_arbitrary_choice_values_by_stringifying_them(self):
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

    def test_calculate_max_length_returns_from_kwargs_if_provided_and_max_choice_length_is_less_than_provided(
            self
    ):
        class TestEnum(Enum):
            FOO = 'foo'
            BAR = 'A' * 100

        field = EnumChoiceField(enum_class=TestEnum)

        result = field._calculate_max_length(choices=field.build_choices(), max_length=150)

        self.assertEqual(150, result)

    def test_calculate_max_length_returns_longest_choice_length_if_length_not_provided_in_kwargs(self):
        class TestEnum(Enum):
            FOO = 'foo'
            BAR = 'A' * 100

        field = EnumChoiceField(enum_class=TestEnum)

        result = field._calculate_max_length(choices=field.build_choices())

        self.assertEqual(100, result)

    def test_calculate_max_length_returns_max_choice_length_if_length_provided_in_kwargs_and_less_than_longest_choice(
        self
    ):
        class TestEnum(Enum):
            FOO = 'foo'
            BAR = 'A' * 100

        field = EnumChoiceField(enum_class=TestEnum)

        result = field._calculate_max_length(choices=field.build_choices(), max_length=10)

        self.assertEqual(100, result)

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

        with self.assertRaises(EnumChoiceFieldException):
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

        with self.assertRaisesMessage(
            EnumChoiceFieldException,
            f'Value NOT_EXISTING not found in {str(CharTestEnum)}'
        ):
            instance.to_python('NOT_EXISTING')


class ModelIntegrationTests(TestCase):
    def test_can_create_object_with_char_base(self):
        instance = StringEnumeratedModel.objects.create(
            enumeration=CharTestEnum.FIRST
        )
        instance.refresh_from_db()

        self.assertEqual(instance.enumeration, CharTestEnum.FIRST)

    def test_can_assign_enumeration_with_char_base(self):
        instance = StringEnumeratedModel.objects.create(
            enumeration=CharTestEnum.FIRST
        )
        instance.refresh_from_db()

        instance.enumeration = CharTestEnum.SECOND
        instance.save()
        instance.refresh_from_db()

        self.assertEqual(instance.enumeration, CharTestEnum.SECOND)

    def test_can_filter_by_enumeration_with_char_base(self):
        first = StringEnumeratedModel.objects.create(
            enumeration=CharTestEnum.FIRST
        )
        second = StringEnumeratedModel.objects.create(
            enumeration=CharTestEnum.SECOND
        )

        first_qs = StringEnumeratedModel.objects.filter(enumeration=CharTestEnum.FIRST)
        second_qs = StringEnumeratedModel.objects.filter(enumeration=CharTestEnum.SECOND)

        self.assertIn(first, first_qs)
        self.assertNotIn(second, first_qs)

        self.assertIn(second, second_qs)
        self.assertNotIn(first, second_qs)

    def test_can_create_object_with_int_base(self):
        instance = IntegerEnumeratedModel.objects.create(
            enumeration=IntTestEnum.FIRST
        )
        instance.refresh_from_db()

        self.assertEqual(instance.enumeration, IntTestEnum.FIRST)

    def test_can_assign_enumeration_with_int_base(self):
        instance = IntegerEnumeratedModel.objects.create(
            enumeration=IntTestEnum.FIRST
        )
        instance.refresh_from_db()

        instance.enumeration = IntTestEnum.SECOND
        instance.save()
        instance.refresh_from_db()

        self.assertEqual(instance.enumeration, IntTestEnum.SECOND)

    def test_can_filter_by_enumeration_with_int_base(self):
        first = IntegerEnumeratedModel.objects.create(
            enumeration=IntTestEnum.FIRST
        )
        second = IntegerEnumeratedModel.objects.create(
            enumeration=IntTestEnum.SECOND
        )

        first_qs = IntegerEnumeratedModel.objects.filter(enumeration=IntTestEnum.FIRST)
        second_qs = IntegerEnumeratedModel.objects.filter(enumeration=IntTestEnum.SECOND)

        self.assertIn(first, first_qs)
        self.assertNotIn(second, first_qs)

        self.assertIn(second, second_qs)
        self.assertNotIn(first, second_qs)

    def test_serialization(self):
        IntegerEnumeratedModel.objects.create(
            enumeration=IntTestEnum.FIRST
        )

        data = serializers.serialize('json', IntegerEnumeratedModel.objects.all())

        expected = '[{"model": "testapp.integerenumeratedmodel", "pk": 1, "fields": {"enumeration": "1"}}]'

        self.assertEqual(expected, data)

    def test_deserialization(self):
        instance = IntegerEnumeratedModel.objects.create(
            enumeration=IntTestEnum.FIRST
        )

        data = serializers.serialize('json', IntegerEnumeratedModel.objects.all())
        objects = list(serializers.deserialize('json', data))

        self.assertEqual(1, len(objects))

        deserialized_instance = objects[0]

        self.assertEqual(instance, deserialized_instance.object)

    def test_object_with_nullable_field_can_be_created(self):
        instance = NullableEnumeratedModel()

        self.assertIsNone(instance.enumeration)

    def test_nullable_field_can_be_set_to_none(self):
        instance = NullableEnumeratedModel(
            enumeration=CharTestEnum.FIRST
        )

        instance.enumeration = None
        instance.save()
        instance.refresh_from_db()

        self.assertIsNone(instance.enumeration)

    def test_non_blank_field_raises_error_on_clean(self):
        instance = NullableEnumeratedModel()

        with self.assertRaisesMessage(
            ValidationError,
            str(EnumChoiceField.default_error_messages['blank'])
        ):
            instance.full_clean()

    def test_blank_field_does_not_raise_error_on_clean(self):
        instance = BlankNullableEnumeratedModel()

        instance.full_clean()

        self.assertIsNone(instance.enumeration)
