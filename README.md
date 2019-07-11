# django-enum-choices

A custom Django choice field to use with [Python enums.](https://docs.python.org/3/library/enum.html)

[![PyPI version](https://badge.fury.io/py/django-enum-choices.svg)](https://badge.fury.io/py/django-enum-choices)

## Table of Contents
- [Installation](#installation)
- [Basic Usage](#basic-usage)
- [Postgres ArrayField Usage](#postgres-arrayfield-usage)
- [Usage with Django Rest Framework](#usage-with-django-rest-framework)
  - [Caveat](#caveat)
- [Serializing PostgreSQL ArrayField](#serializing-postgresql-arrayfield)
- [Customizing readable values](#customizing-readable-values)
- [Implementation details](#implementation-details)
- [Using Python's `enum.auto`](#using-pythons-enumauto)
- [Development](#development)

## Installation

```bash
pip install django-enum-choices
```

## Basic Usage

```python
from django.db import models

from django_enum_choices.fields import EnumChoiceField


from enum import Enum

class MyEnum(Enum):
    A = 'a'
    B = 'b'


class MyModel(models.Model):
    enumerated_field = EnumChoiceField(MyEnum)
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
from django.db import models
from django.contrib.postgres.fields import ArrayField

from django_enum_choices.fields import EnumChoiceField

from enum import Enum

class MyEnum(Enum):
    A = 'a'
    B = 'b'

class MyModelMultiple(models.Model):
    enumerated_field = ArrayField(
        base_field=EnumChoiceField(MyEnum)
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
    enumerated_field = EnumChoiceField(MyEnum)

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
    enumerated_field = EnumChoiceField(MyEnum)

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
    enumerated_field = MultipleEnumChoiceField(MyEnum)

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


## Customizing readable values

If a `get_readable_value` method is provided, `django_enum_choices` will use it to produce the readable values that are written in the database:

```python
class CustomReadableValueEnum(Enum):
    A = 'a'
    B = 'b'

    @classmethod
    def get_readable_value(cls, choice):
        return cls(choice).value.upper()
```

Using the above class as an `enum_class` argument to `django_enum_choices.fields.EnumChoiceField` will produce the choices for the database as `(('a', 'A'), ('b', 'B'))`


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
        return self.value


class CustomObjectEnum(Enum):
    A = Value(1)
    B = Value('B')


class SomeModel(models.Model):
    enumerated_field = EnumChoiceField(CustomObjectEnum)
```

We'll have the following:

* `SomeModel.enumerated_field.choices == (('1', '1'), ('B', 'B'))`
* `SomeModel.enumerated_field.max_length == 3`

## Using Python's `enum.auto`
`enum.auto` can be used for shorthand enumeration definitions:

```python
from enum import Enum, auto

class AutoEnum(Enum):
    A = auto()  # 1
    B = auto()  # 2

class SomeModel(models.Model):
    enumerated_field = EnumChoiceField(Enum)
```

This will result in the following:
* `SomeModel.enumerated_field.choices == (('1', '1'), ('2', '2'))`

**Overridinng `auto` behaviour**
Custom values for enumerations, created by `auto`, can be defined by
subclassing an `Enum` that defines `_generate_next_value_`:

```python
class CustomAutoEnumValueGenerator(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return {
            'A': 'foo',
            'B': 'bar'
        }[name]


class CustomAutoEnum(CustomAutoEnumValueGenerator):
    A = auto()
    B = auto()
```

The above will assign the values mapped in the dictionary as values to attributes in `CustomAutoEnum`.

## Development
**Prerequisites**
* SQLite3
* PostgreSQL server
* Python >= 3.5 virtual environment

```bash
git clone https://github.com/HackSoftware/django-enum-choices.git
cd django_enum_choices
pip install -e .[dev]
```

Linting and running the tests:
```bash
tox
```
