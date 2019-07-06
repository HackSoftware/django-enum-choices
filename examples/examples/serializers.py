from rest_framework import serializers

from django_enum_choices.serializers import (
    EnumChoiceField,
    MultipleEnumChoiceField,
    EnumChoiceModelSerializerMixin
)


from .enumerations import MyEnum
from .models import MyModel, MyModelMultiple


# Standard Serializer
class MySerializer(serializers.Serializer):
    enumerated_field = EnumChoiceField(MyEnum)


# Model Serializer
class MyModelSerializer(serializers.ModelSerializer):
    enumerated_field = EnumChoiceField(MyEnum)

    class Meta:
        model = MyModel
        fields = ('enumerated_field', )


# Model Serializer without field declaration
class ImplicitMyModelSerializer(
    EnumChoiceModelSerializerMixin,
    serializers.ModelSerializer
):
    class Meta:
        model = MyModel
        fields = ('enumerated_field', )


# Multiple Standard Serializer
class MultipleMySerializer(serializers.Serializer):
    enumerated_field = MultipleEnumChoiceField(MyEnum)


# Multiple Model Serializer without field declaration
class ImplicitMultipleMyModelSerializer(
    EnumChoiceModelSerializerMixin,
    serializers.ModelSerializer
):
    class Meta:
        model = MyModelMultiple
        fields = ('enumerated_field', )
