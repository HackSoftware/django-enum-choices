from django.test import TestCase

from django_enum_choices.forms import EnumChoiceField

from .testapp.enumerations import CharTestEnum


class FormFieldTests(TestCase):
    def test_field_instance_creates_choices_correctly(self):
        instance = EnumChoiceField(CharTestEnum)
        choices = instance.build_choices()

        self.assertEqual(
            choices,
            [('first', 'first'),
             ('second', 'second'),
             ('third', 'third')]
        )

    def test_field_instance_creates_choices_correctly_with_custom_choice_builder(self):
        def choice_builder(choice):
            return 'Custom_' + choice.value, choice.value

        instance = EnumChoiceField(CharTestEnum, choice_builder=choice_builder)
        choices = instance.build_choices()

        self.assertEqual(
            choices,
            [('Custom_first', 'first'),
             ('Custom_second', 'second'),
             ('Custom_third', 'third')]
        )
