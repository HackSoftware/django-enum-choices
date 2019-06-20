from enum import Enum

from django.test import TestCase

from django_enum_choices.fields import EnumChoiceFieldBuilder, EnumIntegerField, EnumCharField, EnumChoiceField
from django_enum_choices.exceptions import EnumChoiceFieldException
from .testapp.enumerations import CharTestEnum, IntTestEnum
from .testapp.models import IntegerEnumeratedModel, StringEnumeratedModel


class EnumChoiceFieldBuilderTests(TestCase):
    def test_builder_initializes_string_choice_values(self):
        builder = EnumChoiceFieldBuilder(enum_class=CharTestEnum)

        self.assertEqual(
            builder.enum_class,
            CharTestEnum
        )
        self.assertEqual(
            builder._choices,
            ['first', 'second', 'third']
        )

    def test_builder_initializes_int_choice_values(self):
        builder = EnumChoiceFieldBuilder(enum_class=IntTestEnum)

        self.assertEqual(
            builder.enum_class,
            IntTestEnum
        )
        self.assertEqual(
            builder._choices,
            [1, 2, 3]
        )

    def test_builder_packs_string_choices_correctly(self):
        builder = EnumChoiceFieldBuilder(enum_class=CharTestEnum)

        packed = builder._pack_choices()

        self.assertEqual(
            list(packed),
            [
                ('first', 'first'),
                ('second', 'second'),
                ('third', 'third')
            ]
        )

    def test_builder_packs_int_choices_correctly(self):
        builder = EnumChoiceFieldBuilder(enum_class=IntTestEnum)

        packed = builder._pack_choices()

        self.assertEqual(
            list(packed),
            [
                (1, 1),
                (2, 2),
                (3, 3)
            ]
        )

    def test_get_inferred_base_returns_intfield_instance_when_all_choice_types_are_int(self):
        builder = EnumChoiceFieldBuilder(enum_class=IntTestEnum)

        base = builder.get_inferred_base()

        self.assertIs(base, EnumIntegerField)

    def test_get_inferred_base_returns_charfield_instance_when_all_choice_types_are_str(self):
        builder = EnumChoiceFieldBuilder(enum_class=CharTestEnum)

        base = builder.get_inferred_base()

        self.assertIs(base, EnumCharField)

    def test_get_inferred_base_raises_exception_when_choice_types_differ(self):
        class FailingEnum(Enum):
            FOO = 1
            BAR = '2'

        builder = EnumChoiceFieldBuilder(enum_class=FailingEnum)

        with self.assertRaisesMessage(
            EnumChoiceFieldException,
            'All choices in provided enum class must be of the same type'
        ):

            builder.get_inferred_base()

    def test_calculate_max_length_returns_longest_choice_length_if_max_length_not_in_kwargs_and_longer_than_255(
        self
    ):
        class LongStringEnum(Enum):
            FOO = 'foo'
            BAR = 'A' * 256

        builder = EnumChoiceFieldBuilder(enum_class=LongStringEnum)

        result = builder._calculate_max_length()

        self.assertEqual(result, 256)

    def test_calculate_max_length_returns_255_when_longest_choice_is_less_than_255_and_max_length_not_in_kwargs(
        self
    ):
        class ShortStringEnum(Enum):
            FOO = 'foo'
            BAR = 'bar'

        builder = EnumChoiceFieldBuilder(enum_class=ShortStringEnum)

        result = builder._calculate_max_length()

        self.assertEqual(result, 255)

    def test_calculate_max_length_returns_255_when_max_length_in_kwargs_and_less_than_255(self):
        builder = EnumChoiceFieldBuilder(enum_class=CharTestEnum)

        result = builder._calculate_max_length(max_length=50)

        self.assertEqual(result, 255)

    def test_calculate_max_length_returns_max_length_from_kwargs_more_than_255(self):
        builder = EnumChoiceFieldBuilder(enum_class=CharTestEnum)

        result = builder._calculate_max_length(max_length=256)

        self.assertEqual(result, 256)

    def test_get_swapped_instance_returns_correct_model_field_instance(self):
        with self.subTest('When base is `EnumIntegerField`'):
            builder = EnumChoiceFieldBuilder(enum_class=IntTestEnum)

            instance = builder.get_swapped_instance(base=EnumIntegerField)

            self.assertIsInstance(instance, EnumIntegerField)

        with self.subTest('When base is `EnumCharField`'):
            builder = EnumChoiceFieldBuilder(enum_class=CharTestEnum)

            instance = builder.get_swapped_instance(base=EnumCharField)

            self.assertIsInstance(instance, EnumCharField)


class EnumChoiceFieldTests(TestCase):
    def test_raises_exception_when_enum_class_is_not_enumeration(self):
        class FailingEnum:
            FOO = 'foo'
            BAR = 'bar'

        with self.assertRaisesMessage(
            EnumChoiceFieldException,
            '`enum_class` argument must be a child of `Enum`'
        ):
            EnumChoiceField(enum_class=FailingEnum)

    def test_instance_returns_EnumCharField_when_choices_are_strings(self):
        instance = EnumChoiceField(enum_class=CharTestEnum)

        self.assertIsInstance(instance, EnumCharField)

    def test_instance_returns_EnumIntegerField_when_choices_are_integers(self):
        instance = EnumChoiceField(enum_class=IntTestEnum)

        self.assertIsInstance(instance, EnumIntegerField)

    def test_get_prep_value_returns_primitive_value_when_base_is_integer(self):
        instance = EnumChoiceField(enum_class=IntTestEnum)

        result = instance.get_prep_value(IntTestEnum.FIRST)

        self.assertEqual(result, 1)

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

        result = instance.from_db_value(1, None, None)

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
