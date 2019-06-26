from django.test import TestCase
from django.core import serializers
from django.core.exceptions import ValidationError

from django_enum_choices.fields import EnumChoiceField

from .testapp.enumerations import CharTestEnum, IntTestEnum
from .testapp.models import (
    IntegerEnumeratedModel,
    StringEnumeratedModel,
    NullableEnumeratedModel,
    BlankNullableEnumeratedModel,
    EnumChoiceFieldWithDefaultModel
)


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

    def test_non_enum_value_raises_error_on_clean(self):
        instance = StringEnumeratedModel.objects.create(
            enumeration=CharTestEnum.FIRST
        )

        instance.enumeration = "foo"

        with self.assertRaises(
            ValidationError
        ):
            instance.full_clean()

    def test_default_value_is_used(self):
        instance = EnumChoiceFieldWithDefaultModel.objects.create()

        self.assertEqual(
            EnumChoiceFieldWithDefaultModel._meta.get_field('enumeration').default,
            instance.enumeration
        )
