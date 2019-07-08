from .enumerations import MyEnum
from .models import MyModel, MyModelMultiple
from .serializers import (
    MySerializer,
    MyModelSerializer,
    ImplicitMyModelSerializer,
    MultipleMySerializer,
    ImplicitMultipleMyModelSerializer
)


# Object Creation
def create_instance():
    return MyModel.objects.create(enumerated_field=MyEnum.A)


# Overriding field value
def update_instance():
    instance = create_instance()
    instance.enumerated_field = MyEnum.B

    instance.save()

    return instance


# Object creation with multiple field
def create_instance_with_multiple_field():
    return MyModelMultiple.objects.create(enumerated_field=[MyEnum.A, MyEnum.B])


# Overriding multiple field value
def update_instance_with_multiple_field():
    instance = create_instance_with_multiple_field()
    instance.enumerated_field = [MyEnum.B]

    instance.save()

    return instance


# QuerySet filtering
def filter_queryset():
    return MyModel.objects.filter(enumerated_field=MyEnum.A)


# Serializer usage
def serialize_value():
    serializer = MySerializer({
        'enumerated_field': MyEnum.A
    })

    return serializer.data


def deserialize_value():
    serializer = MySerializer(data={
        'enumerated_field': 'a'
    })
    serializer.is_valid()

    return serializer.validated_data


# Explicit ModelSerializer usage
def serialize_model_from_explicit_serializer():
    instance = create_instance()
    serializer = MyModelSerializer(instance)

    return serializer.data


def create_model_from_explicit_serializer():
    serializer = MyModelSerializer(data={
        'enumerated_field': 'a'
    })
    serializer.is_valid()

    return serializer.save()


# Implicit ModelSerializer usage
def serialize_model_from_implicit_serializer():
    instance = create_instance()
    serializer = ImplicitMyModelSerializer(instance)

    return serializer.data


def create_model_from_implicit_serializer():
    serializer = ImplicitMyModelSerializer(data={
        'enumerated_field': 'a'
    })
    serializer.is_valid()

    return serializer.save()


# Multiple Standard Serializer Usage
def serialize_multiple_value():
    serializer = MultipleMySerializer({
        'enumerated_field': [MyEnum.A, MyEnum.B]
    })

    return serializer.data


def deserialize_multiple_value():
    serializer = MultipleMySerializer(data={
        'enumerated_field': ['a', 'b']
    })
    serializer.is_valid()

    return serializer.validated_data


# Implicit Multiple ModelSerializer usage
def serialize_model_from_multiple_field_serializer():
    instance = create_instance_with_multiple_field()
    serializer = ImplicitMultipleMyModelSerializer(instance)

    return serializer.data


def create_model_from_multiple_field_serializer():
    serializer = ImplicitMultipleMyModelSerializer(data={
        'enumerated_field': ['a', 'b']
    })
    serializer.is_valid()

    return serializer.save()
