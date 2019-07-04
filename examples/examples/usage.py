from .enumerations import MyEnum
from .models import MyModel
from .serializers import MySerializer, MyModelSerializer


# Object Creation
def create_instance():
    return MyModel.objects.create(enumerated_field=MyEnum.A)


# Overriding field value
def update_instance():
    instance = MyModel.objects.create(enumerated_field=MyEnum.A)
    instance.enumerated_field = MyEnum.B

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
    assert serializer.is_valid()

    return serializer.validated_data


# ModelSerializer usage
def serialize_model():
    instance = create_instance()
    serializer = MyModelSerializer(instance)

    return serializer.data


def create_model_from_serializer():
    serializer = MyModelSerializer(data={
        'enumerated_field': 'a'
    })
    serializer.is_valid()

    return serializer.save()
