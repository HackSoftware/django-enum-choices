from django.test import TestCase

from rest_framework import serializers

from django_enum_choices.serializers import EnumChoiceField, EnumChoiceModelSerializerMixin
from .testapp.models import StringEnumeratedModel
from .testapp.enumerations import CharTestEnum


class SerializerIntegrationTests(TestCase):
    class Serializer(serializers.Serializer):
        enumeration = EnumChoiceField(enum_class=CharTestEnum)

    def test_field_value_is_serialized_correctly(self):
        serializer = self.Serializer({'enumeration': CharTestEnum.FIRST})

        result = serializer.data['enumeration']

        self.assertEqual(result, 'first')

    def test_field_is_deserialized_correctly(self):
        serializer = self.Serializer(data={'enumeration': 'first'})
        serializer.is_valid()

        result = serializer.validated_data['enumeration']

        self.assertEqual(result, CharTestEnum.FIRST)


class ModelSerializerIntegrationTests(TestCase):
    class Serializer(serializers.ModelSerializer):
        enumeration = EnumChoiceField(enum_class=CharTestEnum)

        class Meta:
            model = StringEnumeratedModel
            fields = ('enumeration', )

    def test_field_value_is_serialized_correctly(self):
        instance = StringEnumeratedModel.objects.create(
            enumeration=CharTestEnum.FIRST
        )

        serializer = self.Serializer(instance)

        result = serializer.data['enumeration']

        self.assertEqual(result, 'first')

    def test_field_is_deserialized_correctly(self):
        serializer = self.Serializer(data={'enumeration': 'first'})
        serializer.is_valid()

        result = serializer.validated_data['enumeration']

        self.assertEqual(result, CharTestEnum.FIRST)

    def test_field_is_serialized_correctly_when_using_serializer_mixin(self):
        class Serializer(EnumChoiceModelSerializerMixin, serializers.ModelSerializer):
            class Meta:
                model = StringEnumeratedModel
                fields = ('enumeration', )

        instance = StringEnumeratedModel.objects.create(
            enumeration=CharTestEnum.FIRST
        )
        serializer = Serializer(instance)
        result = serializer.data['enumeration']

        self.assertEqual('first', result)

    def test_field_is_deserialized_correctly_when_using_serializer_mixin(self):
        class Serializer(EnumChoiceModelSerializerMixin, serializers.ModelSerializer):
            class Meta:
                model = StringEnumeratedModel
                fields = ('enumeration', )

        serializer = self.Serializer(data={'enumeration': 'first'})
        serializer.is_valid()

        result = serializer.validated_data['enumeration']

        self.assertEqual(CharTestEnum.FIRST, result)

    def test_instance_is_created_successfully_after_model_serializer_create(self):
        class Serializer(EnumChoiceModelSerializerMixin, serializers.ModelSerializer):
            class Meta:
                model = StringEnumeratedModel
                fiedls = ('enumeration', )

        current_instance_count = StringEnumeratedModel.objects.count()

        serializer = self.Serializer(data={'enumeration': 'first'})
        serializer.is_valid()

        instance = serializer.create(serializer.validated_data)

        self.assertEqual(
            current_instance_count + 1,
            StringEnumeratedModel.objects.count()
        )
        self.assertEqual(
            CharTestEnum.FIRST,
            instance.enumeration
        )

    def test_instance_is_update_successfully_after_model_serializer_update(self):
        class Serializer(EnumChoiceModelSerializerMixin, serializers.ModelSerializer):
            class Meta:
                model = StringEnumeratedModel
                fiedls = ('enumeration', )

        instance = StringEnumeratedModel.objects.create(
            enumeration=CharTestEnum.FIRST
        )

        serializer = self.Serializer(data={'enumeration': 'second'})
        serializer.is_valid()

        serializer.update(instance, serializer.validated_data)
        instance.refresh_from_db()

        self.assertEqual(
            CharTestEnum.SECOND,
            instance.enumeration
        )

    def test_serializer_is_not_valid_when_field_is_required_and_not_provided(self):
        class Serializer(serializers.Serializer):
            enumeration = EnumChoiceField(
                enum_class=CharTestEnum
            )

        serializer = Serializer(data={})

        self.assertFalse(serializer.is_valid())

    def test_serializer_is_valid_when_field_is_required_and_provided(self):
        class Serializer(serializers.Serializer):
            enumeration = EnumChoiceField(
                enum_class=CharTestEnum
            )

        serializer = Serializer(data={'enumeration': 'first'})

        self.assertTrue(serializer.is_valid)

    def test_serializer_does_not_add_field_to_validated_data_when_not_required_and_not_provided(self):
        class Serializer(serializers.Serializer):
            enumeration = EnumChoiceField(
                enum_class=CharTestEnum,
                required=False
            )

        serializer = Serializer(data={})
        is_valid = serializer.is_valid()

        self.assertTrue(is_valid)
        self.assertNotIn(
            'enumeration',
            serializer.validated_data.keys()
        )

    def test_serializer_adds_field_to_validated_data_when_not_required_and_provided(self):
        class Serializer(serializers.Serializer):
            enumeration = EnumChoiceField(
                enum_class=CharTestEnum,
                required=False
            )

        serializer = Serializer(data={'enumeration': 'first'})
        is_valid = serializer.is_valid()

        self.assertTrue(is_valid)
        self.assertIn(
            'enumeration',
            serializer.validated_data.keys()
        )

    def test_serializer_is_not_valid_when_field_is_not_nullable_and_value_is_none(self):
        class Serializer(serializers.Serializer):
            enumeration = EnumChoiceField(
                enum_class=CharTestEnum
            )

        serializer = Serializer(data={'enumeration': None})

        self.assertFalse(serializer.is_valid())

    def test_serializer_is_valid_when_field_is_nullable_and_value_is_none(self):
        class Serializer(serializers.Serializer):
            enumeration = EnumChoiceField(
                enum_class=CharTestEnum,
                allow_null=True
            )

        serializer = Serializer(data={'enumeration': None})

        self.assertTrue(serializer.is_valid())
