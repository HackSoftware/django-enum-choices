from django.test import TestCase
from django import forms

from django_enum_choices.forms import EnumChoiceField

from .testapp.enumerations import CharTestEnum
from .testapp.models import StringEnumeratedModel, CustomChoiceBuilderEnumeratedModel


def custom_choice_builder(choice):
    return 'Custom_' + choice.value, choice.value


class FormIntegrationTests(TestCase):
    class StandardEnumForm(forms.Form):
        enumerated_field = EnumChoiceField(CharTestEnum)

    class CustomChoiceBuilderEnumForm(forms.Form):
        enumerated_field = EnumChoiceField(
            CharTestEnum,
            choice_builder=custom_choice_builder
        )

    def test_value_is_cleaned_successfully_when_value_is_valid(self):
        form = self.StandardEnumForm({
            'enumerated_field': 'first'
        })

        self.assertTrue(form.is_valid())
        self.assertEqual(
            CharTestEnum.FIRST,
            form.cleaned_data['enumerated_field']
        )

    def test_form_is_not_valid_when_value_is_not_in_enum_class(self):
        form = self.StandardEnumForm({
            'enumerated_field': 'not_valid'
        })

        expected_error = EnumChoiceField.default_error_messages['invalid_choice'] % {'value': 'not_valid'}

        self.assertFalse(form.is_valid())
        self.assertIn(expected_error, form.errors.get('enumerated_field', []))

    def test_form_is_not_valid_when_value_is_none_and_field_is_required(self):
        form = self.StandardEnumForm({
            'enumerated_field': None
        })

        expected_error = 'This field is required.'

        self.assertFalse(form.is_valid())
        self.assertIn(expected_error, form.errors.get('enumerated_field', []))

    def test_form_is_valid_when_value_is_none_and_field_is_not_required(self):
        class NonRequiredForm(forms.Form):
            enumerated_field = EnumChoiceField(CharTestEnum, required=False)

        form = NonRequiredForm({
            'enumerated_field': None
        })

        self.assertTrue(form.is_valid())
        self.assertEqual(None, form.cleaned_data['enumerated_field'])

    def test_form_is_valid_when_value_is_valid_and_field_uses_custom_choice_builder(self):
        form = self.CustomChoiceBuilderEnumForm({
            'enumerated_field': 'Custom_first'
        })

        self.assertTrue(form.is_valid())
        self.assertEqual(
            CharTestEnum.FIRST,
            form.cleaned_data['enumerated_field']
        )

    def test_form_is_not_valid_when_value_is_invalid_and_field_uses_custom_choice_builder(self):
        form = self.CustomChoiceBuilderEnumForm({
            'enumerated_field': 'first'
        })

        expected_error = EnumChoiceField.default_error_messages['invalid_choice'] % {'value': 'first'}

        self.assertFalse(form.is_valid())
        self.assertIn(expected_error, form.errors['enumerated_field'])


class ModelFormIntegrationTests(TestCase):
    class StandardEnumForm(forms.ModelForm):
        class Meta:
            model = StringEnumeratedModel
            fields = ('enumeration', )

    class CustomChoiceBuilderEnumForm(forms.ModelForm):
        class Meta:
            model = CustomChoiceBuilderEnumeratedModel
            fields = ('enumeration', )

    def test_form_is_valid_when_value_is_valid(self):
        form = self.StandardEnumForm({
            'enumeration': 'first'
        })

        self.assertTrue(form.is_valid())
        self.assertEqual(CharTestEnum.FIRST, form.cleaned_data['enumeration'])

    def test_form_is_invalid_when_value_is_not_from_choices(self):
        form = self.StandardEnumForm({
            'enumeration': 'not_valid'
        })

        expected_error = EnumChoiceField.default_error_messages['invalid_choice'] % {'value': 'not_valid'}

        self.assertFalse(form.is_valid())
        self.assertIn(expected_error, form.errors.get('enumeration', []))

    def test_form_is_valid_when_value_is_valid_and_form_uses_custom_choice_builder(self):
        form = self.CustomChoiceBuilderEnumForm({
            'enumeration': 'Custom_first'
        })

        self.assertTrue(form.is_valid())
        self.assertEqual(CharTestEnum.FIRST, form.cleaned_data['enumeration'])

    def test_form_is_invalid_when_value_is_not_from_choices_and_form_uses_custom_choice_builder(self):
        form = self.CustomChoiceBuilderEnumForm({
            'enumeration': 'first'
        })

        self.assertFalse(form.is_valid())

        expected_error = EnumChoiceField.default_error_messages['invalid_choice'] % {'value': 'first'}
        self.assertIn(expected_error, form.errors.get('enumeration', []))

    def test_saving_model_form_creates_instance(self):
        form = self.CustomChoiceBuilderEnumForm({
            'enumeration': 'Custom_first'
        })

        current_instance_count = CustomChoiceBuilderEnumeratedModel.objects.count()

        self.assertTrue(form.is_valid())

        instance = form.save(commit=True)

        self.assertEqual(
            current_instance_count + 1,
            CustomChoiceBuilderEnumeratedModel.objects.count()
        )
        self.assertEqual(
            CharTestEnum.FIRST,
            instance.enumeration
        )
