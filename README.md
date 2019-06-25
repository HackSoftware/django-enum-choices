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

class FooBarEnumeration(Enum):
    FOO = 'foo'
    BAR = 'bar'


class MyModel(models.Model):
    foo_bar_field = EnumChoiceField(FooBarEnumeration)
```

**Model creation**

```python
instance = MyModel.objects.create(foo_bar_field=FooBarEnumeration.BAR)
```

**Changing enum values**

```python
instance.foo_bar_field = FooBarEnumeration.FOO
instance.save()
```

**Filtering**

```python
MyModel.objects.filter(foo_bar_field=FooBarEnumeration.FOO)
```

## Usage with Django Rest Framework

```python
from rest_framework import serializers

from django_enum_choices.serializers import EnumChoiceField

class MyModelSerializer(serializers.ModelSerializer):
    foo_bar_field = EnumChoiceField(FooBarEnumeration)

    class Meta:
        model = MyModel
        fields = ('foo_bar_field', )
```

In `python manage.py shell`:

```
In [1]: instance = MyModel.objects.create(foo_bar_field=FooBarEnumeration.BAR)
In [2]: MyModelSerializer(instance).data
Out[2]: {'foo_bar_field': 'bar'}
```

### Caveat

If you don't explicitly specify the `foo_bar_field = EnumChoiceField(FooBarEnumeration)`, then you need to include the `EnumChoiceModelSerializerMixin`:

```python
from rest_framework import serializers

from django_enum_choices.serializers import EnumChoiceModelSerializerMixin

class MyModelSerializer(EnumChoiceModelSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = MyModel
        fields = ('foo_bar_field', )
```

By default `ModelSerializer.build_standard_field` coerces any field that has a model field with choices to `ChoiceField` wich returns the value directly.

Since enum values resemble `EnumClass.ENUM_INSTANCE` they won't be able to be encoded by the `JSONEncoder` when being passed to a `Response`.

That's why we need the mixin.

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
