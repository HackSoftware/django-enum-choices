# django-enum-choices

**Library is still work in progress & unstable. When officially launched, we'll announce it.**

A custom Django choice field to use with [Python enums.](https://docs.python.org/3/library/enum.html)

## Installation

```bash
pip install django_enum_choices
```

## Basic Usage

```python
from django import models

from django_enum_choices.fields import EnumChoiceField


from enum import Enum

class MyEnum(Enum):
    A = 'a'
    B = 'b'


class MyModel(models.Model):
    enumerated_field = EnumChoiceField(enum_class=MyEnum)
```

**Model creation**

```python
instance = MyModel.objects.create(enumerated_field=MyEnum.A)
```

**Changing enum values**

```python
instance.enumerated_field = MyEnum.B
instance.save()
```

**Filtering**

```python
MyModel.objects.filter(enumerated_field=MyEnum.A)
```

## Postgres ArrayField Usage

```python
from django import models
from django.contrib.postgres.fields import ArrayField

from django_enum_choices.fields import EnumChoiceField

from enum import Enum

class MyEnum(Enum):
    A = 'a'
    B = 'b'

class MyModelMultiple(models.Model):
    enumerated_field = ArrayField(
        base_field=EnumChoiceField(enum_class=MyEnum)
    )
```

**Model Creation**

```python
instance = MyModelMultiple.objects.create(enumerated_field=[MyEnum.A, MyEnum.B])
```

**Changing enum values**

```python
instance.enumerated_field = [MyEnum.B]
instance.save()
```

## Usage with Django Rest Framework

**Using a subclass of `serializers.Serializer`**

```python
from rest_framework import serializers

from django_enum_choices.serializers import EnumChoiceField

class MySerializer(serializers.Serializer):
    enumerated_field = EnumChoiceField(enum_class=MyEnum)

# Serialization:
serializer = MySerializer({
    'enumerated_field': MyEnum.A
})
data = serializer.data  # {'enumerated_field': 'a'}

# Deserialization:
serializer = MySerializer(data={
    'enumerated_field': 'a'
})
serializer.is_valid()
data = serializer.validated_data  # OrderedDict([('enumerated_field', <MyEnum.A: 'a'>)])
```

**Using a subclass of `serializers.ModelSerializer`**

```python
from rest_framework import serializers

from django_enum_choices.serializers import EnumChoiceField

class MyModelSerializer(serializers.ModelSerializer):
    enumerated_field = EnumChoiceField(enum_class=MyEnum)

    class Meta:
        model = MyModel
        fields = ('enumerated_field', )

# Serialization:
instance = MyModel.objects.create(enumerated_field=MyEnum.A)
serializer = MyModelSerializer(instance)
data = serializer.data  # {'enumerated_field': 'a'}

# Saving:
serializer = MyModelSerializer(data={
    'enumerated_field': 'a'
})
serializer.is_valid()
serializer.save()
```

### Caveat

If you don't explicitly specify the `enumerated_field = EnumChoiceField(MyEnum)`, then you need to include the `EnumChoiceModelSerializerMixin`:

```python
from rest_framework import serializers

from django_enum_choices.serializers import EnumChoiceModelSerializerMixin

class ImplicitMyModelSerializer(
    EnumChoiceModelSerializerMixin,
    serializers.ModelSerializer
):
    class Meta:
        model = MyModel
        fields = ('enumerated_field', )
```

By default `ModelSerializer.build_standard_field` coerces any field that has a model field with choices to `ChoiceField` which returns the value directly.

Since enum values resemble `EnumClass.ENUM_INSTANCE` they won't be able to be encoded by the `JSONEncoder` when being passed to a `Response`.

That's why we need the mixin.

## Serializing PostgreSQL ArrayField
`django-enum-choices` exposes a `MultipleEnumChoiceField` that can be used for serializing arrays of enumerations.

**Using a subclass of `serializers.Serializer`**

```python
from rest_framework import serializers

from django_enum_choices.serializers import MultipleEnumChoiceField

class MultipleMySerializer(serializers.Serializer):
    enumerated_field = MultipleEnumChoiceField(enum_class=MyEnum)

# Serialization:
serializer = MultipleMySerializer({
    'enumerated_field': [MyEnum.A, MyEnum.B]
})
data = serializer.data  # {'enumerated_field': ['a', 'b']}

# Deserialization:
serializer = MultipleMySerializer(data={
    'enumerated_field': ['a', 'b']
})
serializer.is_valid()
data = serializer.validated_data  # OrderedDict([('enumerated_field', [<MyEnum.A: 'a'>, <MyEnum.B: 'b'>])])
```

**Using a subclass of `serializers.ModelSerializer`**

```python
class ImplicitMultipleMyModelSerializer(
    EnumChoiceModelSerializerMixin,
    serializers.ModelSerializer
):
    class Meta:
        model = MyModelMultiple
        fields = ('enumerated_field', )

# Serialization:
instance = MyModelMultiple.objects.create(enumerated_field=[MyEnum.A, MyEnum.B])
serializer = ImplicitMultipleMyModelSerializer(instance)
data = serializer.data  # {'enumerated_field': ['a', 'b']}

# Saving:
serializer = ImplicitMultipleMyModelSerializer(data={
    'enumerated_field': ['a', 'b']
})
serializer.is_valid()
serializer.save()
```

The `EnumChoiceModelSerializerMixin` does not need to be used if `enumerated_field` is defined on the serializer class explicitly.


## Implementation details

* `EnumChoiceField` is a subclass of `CharField`.
* Only subclasses of `Enum` are valid arguments for `EnumChoiceField`.
* `choices` are generated from the values of the enumeration, like `(str(value), str(value))`, meaning you can put any valid Python object there.
* `max_length`, if passed, is ignored. `max_length` is automatically calculated from the longest choice.


For example, lets have the following case:

```python
class Value:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Enumeration(Enum):
    A = Value(1)
    B = Value('foo')


class SomeModel(models.Model):
    enumeration = EnumChoiceField(Enumeration)
```

We'll have the following:

* `SomeModel.enumeration.choices == (('1', '1'), ('foo', 'foo'))`
* `SomeModel.enumeration.max_length == 3`

## Development

```bash
git clone https://github.com/HackSoftware/django-enum-choices.git
pip install -e some-directory/django_enum_choices
```
