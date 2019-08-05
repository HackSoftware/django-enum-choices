from enum import Enum

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.admin.utils import display_for_field

from django_enum_choices.fields import EnumChoiceField
from django_enum_choices.exceptions import EnumChoiceFieldException
from django_enum_choices.choice_builders import value_value
from django_enum_choices.forms import EnumChoiceField as EnumChoiceFormField

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
        self.assertEqual(instance._original_choice_builder, new_instance._original_choice_builder)

    def test_choice_builder_is_used_when_callable(self):
        class TestEnum(Enum):
            A = 1
            B = 2

        def choice_builder(enum_instance):
            if enum_instance == TestEnum.A:
                return 1, 'A'

            if enum_instance == TestEnum.B:
                return 2, 'B'

        instance = EnumChoiceField(enum_class=TestEnum, choice_builder=choice_builder)

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

    def test_flatchoices_returns_enumerations_as_choice_keys(self):
        instance = EnumChoiceField(enum_class=CharTestEnum)

        result = instance.flatchoices

        for choice, _ in result:
            self.assertIsInstance(choice, CharTestEnum)

    def test_flatchoices_returns_readable_value_as_choice_value_when_autogenerated(self):
        instance = EnumChoiceField(enum_class=CharTestEnum)

        result = instance.flatchoices

        for choice, readable in result:
            self.assertEqual(
                CharTestEnum(choice).value,
                readable
            )

    def test_flatchoices_returns_readable_value_as_choice_value_when_choice_builder_is_redefined(self):
        class TestEnum(Enum):
            FOO = 'foo'
            BAR = 'bar'

        def choice_builder(choice):
            return choice.value, choice.value.upper()

        instance = EnumChoiceField(enum_class=TestEnum, choice_builder=choice_builder)

        result = instance.flatchoices

        for choice, readable in result:
            self.assertEqual(
                choice_builder(TestEnum(choice))[1],
                readable
            )

    def test_display_for_field_returns_readable_value_when_autogenerated(self):
        instance = EnumChoiceField(enum_class=CharTestEnum)

        result = display_for_field(CharTestEnum.FIRST, instance, None)

        self.assertEqual(CharTestEnum.FIRST.value, result)

    def test_display_for_field_returns_readable_value_when_choice_builder_is_redefined(self):
        class TestEnum(Enum):
            FOO = 'foo'
            BAR = 'bar'

        def choice_builder(choice):
            return choice.value, choice.value.upper()

        instance = EnumChoiceField(enum_class=TestEnum, choice_builder=choice_builder)

        result = display_for_field(TestEnum.FOO, instance, None)

        self.assertEqual(choice_builder(TestEnum.FOO)[1], result)

    def test_display_for_field_returns_empty_display_when_value_is_none(self):
        EMPTY_DISPLAY = 'EMPTY'

        instance = EnumChoiceField(enum_class=CharTestEnum)

        result = display_for_field(None, instance, EMPTY_DISPLAY)

        self.assertEqual(EMPTY_DISPLAY, result)

    def test_validate_raises_error_when_field_is_not_null_and_value_is_none(self):
        instance = EnumChoiceField(enum_class=CharTestEnum)

        with self.assertRaisesMessage(
            ValidationError,
            str(instance.error_messages['null'])
        ):
            instance.validate(None)

    def test_validate_raises_error_when_field_is_not_blank_and_value_is_empty(self):
        instance = EnumChoiceField(enum_class=CharTestEnum)

        with self.assertRaisesMessage(
            ValidationError,
            str(instance.error_messages['blank'])
        ):
            instance.validate('')

    def test_validate_raises_error_when_value_is_not_from_enum_class(self):
        instance = EnumChoiceField(enum_class=CharTestEnum)

        expected = instance.error_messages['invalid_choice'] % {'value': 'foo'}

        with self.assertRaisesMessage(
            ValidationError,
            expected
        ):
            instance.validate('foo')

    def test_get_choice_builder_raises_exception_when_choice_builder_is_not_callable(self):
        class TestEnum(Enum):
            A = 1
            B = 2

        choice_builder = 'choice_builder'

        with self.assertRaisesMessage(
            EnumChoiceFieldException,
            '`TestEnum.choice_builder` must be a callable'
        ):
            instance = EnumChoiceField(enum_class=TestEnum)

            instance._get_choice_builder(choice_builder)

    def test_value_value_is_used_when_choice_builder_is_not_provided(self):
        instance = EnumChoiceField(enum_class=CharTestEnum)

        self.assertEqual(instance._original_choice_builder, value_value)

    def test_custom_choice_builder_is_used_when_provided_and_callable(self):
        def choice_builder(choice):
            return choice.name, choice.value

        instance = EnumChoiceField(
            enum_class=CharTestEnum,
            choice_builder=choice_builder
        )

        self.assertEqual(
            instance._original_choice_builder,
            choice_builder
        )

    def test_build_choices_raises_exception_when_not_all_values_are_strings(self):
        instance = EnumChoiceField(enum_class=CharTestEnum)
        instance.choice_builder = lambda x: (1, 1)

        with self.assertRaisesMessage(
            EnumChoiceFieldException,
            'Received type {} on key inside choice: (1, 1).\n'.format(int) +
            'All choices generated from {} must be strings.'.format(CharTestEnum)
        ):
            instance.build_choices()

    def test_get_choices_returns_choices_in_correct_format(self):
        instance = EnumChoiceField(enum_class=CharTestEnum)

        result = instance.get_choices()

        self.assertEqual(len(result), 4)
        self.assertIn(instance.choice_builder(CharTestEnum.FIRST), result)
        self.assertIn(instance.choice_builder(CharTestEnum.SECOND), result)
        self.assertIn(instance.choice_builder(CharTestEnum.THIRD), result)

    def test_formfield_returns_enum_choice_form_field_instance(self):
        instance = EnumChoiceField(enum_class=CharTestEnum)

        result = instance.formfield()

        self.assertIsInstance(result, EnumChoiceFormField)
