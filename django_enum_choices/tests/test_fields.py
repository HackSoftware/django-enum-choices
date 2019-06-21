from enum import Enum

from django.test import TestCase

from django_enum_choices.fields import EnumChoiceField
from django_enum_choices.exceptions import EnumChoiceFieldException
from .testapp.enumerations import CharTestEnum, IntTestEnum
from .testapp.models import IntegerEnumeratedModel, StringEnumeratedModel


class EnumChoiceFieldTests(TestCase):
    def test_field_initializes_string_choice_values(self):
        field = EnumChoiceField(enum_class=CharTestEnum)

        self.assertEqual(
            field.enum_class,
            CharTestEnum
        )
        self.assertEqual(
            field.choices,
            [(choice, choice) for choice in ['first', 'second', 'third']]
        )

    def test_builder_initializes_int_choice_values(self):
        field = EnumChoiceField(enum_class=IntTestEnum)

        self.assertEqual(
            field.enum_class,
            IntTestEnum
        )
        self.assertEqual(
            field.choices,
            [(choice, choice) for choice in ['1', '2', '3']]
        )

    def test_builder_packs_string_choices_correctly(self):
        field = EnumChoiceField(enum_class=CharTestEnum)

        packed = field._pack_choices()

        self.assertEqual(
            list(packed),
            [
                ('first', 'first'),
                ('second', 'second'),
                ('third', 'third')
            ]
        )

    def test_builder_packs_int_choices_correctly(self):
        field = EnumChoiceField(enum_class=IntTestEnum)

        packed = field._pack_choices()

        self.assertEqual(
            list(packed),
            [
                ('1', '1'),
                ('2', '2'),
                ('3', '3')
            ]
        )

    def test_calculate_max_length_returns_longest_choice_length_if_max_length_not_in_kwargs_and_longer_than_255(
        self
    ):
        class LongStringEnum(Enum):
            FOO = 'foo'
            BAR = 'A' * 256

        field = EnumChoiceField(enum_class=LongStringEnum)

        result = field._calculate_max_length(choices=field.build_choices())

        self.assertEqual(result, 256)

    def test_calculate_max_length_returns_255_when_longest_choice_is_less_than_255_and_max_length_not_in_kwargs(
        self
    ):
        class ShortStringEnum(Enum):
            FOO = 'foo'
            BAR = 'bar'

        field = EnumChoiceField(enum_class=ShortStringEnum)

        result = field._calculate_max_length(choices=field.build_choices())

        self.assertEqual(result, 255)

    def test_calculate_max_length_returns_255_when_max_length_in_kwargs_and_less_than_255(self):
        field = EnumChoiceField(enum_class=CharTestEnum)

        result = field._calculate_max_length(max_length=50, choices=field.build_choices())

        self.assertEqual(result, 255)

    def test_calculate_max_length_returns_max_length_from_kwargs_more_than_255(self):
        field = EnumChoiceField(enum_class=CharTestEnum)

        result = field._calculate_max_length(max_length=256, choices=field.build_choices())

        self.assertEqual(result, 256)

    def test_raises_exception_when_enum_class_is_not_enumeration(self):
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

    def test_from_db_value_returns_None_when_value_is_none(self):
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
