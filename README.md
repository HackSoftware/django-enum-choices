# django-enum-choices

**Library is still work in progress & unstable. When officially launched, we'll announce it.**

A custom Django field able to use subclasses of Python's internal `Enum` class as choices

## Installation
```bash
git clone https://github.com/slavov-v/django-enum-choices.git
pip install -e some-directory/django_enum_choices
```

## Basic Usage
```python
# enums.py

from enum import Enum

class FooBarEnumeration(Enum):
    FOO = 'foo'
    BAR = 'bar'
```

```python
# models.py

from django import models

from django_enum_choices.fields import EnumChoiceField

from .enums import FooBarEnumeration

class MyModel(models.Model):
    foo_bar_field = EnumChoiceField(enum_class=FooBarEnumeration)
```

```
# python manage.py shell

In [1]: instance = MyModel.objects.create(foo_bar_field=FooBarEnumeration.BAR)
In [2]: instance.foo_bar_field
Out[2]: <FooBarEnumeration.BAR: 'bar'>
```

## Usage with `Django Rest Framework`
```python
# serializers.py

from rest_framework import serializers

from django_enum_choices.serializers import EnumChoiceField

class MyModelSerializer(serializers.ModelSerializer):
    foo_bar_field = EnumChoiceField(enum_class=FooBarEnumeration)

    class Meta:
        model = MyModel
        fields = ('foo_bar_field', )
```

```
# python manage.py shell

In [1]: instance = MyModel.objects.create(foo_bar_field=FooBarEnumeration.BAR)
In [2]: MyModelSerializer(instance).data
Out[2]: {'foo_bar_field': 'bar'}
```
