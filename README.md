# django-enum-choices (DEPRECATED)

A custom Django choice field to use with [Python enums.](https://docs.python.org/3/library/enum.html)

[![PyPI version](https://badge.fury.io/py/django-enum-choices.svg)](https://badge.fury.io/py/django-enum-choices)

## ⚠️ Disclaimer ⚠️

Starting with version 3.0, Django started supporting [Enumerations for model field choices](https://docs.djangoproject.com/en/dev/releases/3.0/#enumerations-for-model-field-choices) and we recommend using this as a native Django feature, instead of `django-enum-choices`

**If you are using `django-enum-choices` and you want to upgrade your project to Django >= `3.0` you can refer to the guide in the wiki: [Migrating to Django 3](https://github.com/HackSoftware/django-enum-choices/wiki/Migrating-to-Django-3)**

## Table of Contents

- [django-enum-choices](#django-enum-choices)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Basic Usage](#basic-usage)
  - [Choice builders](#choice-builders)
  - [Changing/Removing options from enumerations](#changingremoving-options-from-enumerations)
    - [Changing options](#changing-options)
    - [Removing options](#removing-options)
  - [Usage inside the admin panel](#usage-in-the-admin-panel)
  - [Usage with forms](#usage-with-forms)
    - [Usage with `django.forms.ModelForm`](#usage-with-djangoformsmodelform)
    - [Usage with `django.forms.Form`](#usage-with-djangoformsform)
  - [Usage with `django-filter`](#usage-with-django-filter)
    - [By using a `Meta` inner class and inheriting from `EnumChoiceFilterMixin`](#by-using-a-meta-inner-class-and-inheriting-from-enumchoicefiltermixin)
    - [By declaring the field explicitly on the `FilterSet`](#by-declaring-the-field-explicitly-on-the-filterset)
  - [Postgres ArrayField Usage](#postgres-arrayfield-usage)
  - [Usage with Django Rest Framework](#usage-with-django-rest-framework)
    - [Using `serializers.ModelSerializer` with `EnumChoiceModelSerializerMixin`](#using-serializersmodelserializer-with-enumchoicemodelserializermixin)
    - [Using `serializers.ModelSerializer` without `EnumChoiceModelSerializerMixin`](#using-serializersmodelserializer-without-enumchoicemodelserializermixin)
    - [Using a subclass of `serializers.Serializer`](#using-a-subclass-of-serializersserializer)
    - [Serializing PostgreSQL ArrayField](#serializing-postgresql-arrayfield)
  - [Implementation details](#implementation-details)
  - [Using Python's `enum.auto`](#using-pythons-enumauto)
  - [Development](#development)

## Installation

```bash
pip install django-enum-choices
```

## Basic Usage

```python
from enum import Enum

from django.db import models

from django_enum_choices.fields import EnumChoiceField


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

## Choice builders

`EnumChoiceField` extends `CharField` and generates choices internally. Each choice is generated using something, called a `choice_builder`.

A choice builder function looks like that:

```python
def choice_builder(enum: Enum) -> Tuple[str, str]:
    # Some implementation
```

If a `choice_builder` argument is passed to a model's `EnumChoiceField`, `django_enum_choices` will use it to generate the choices.
The `choice_builder` must be a callable that accepts an enumeration choice and returns a tuple,
containing the value to be saved and the readable value.

By default `django_enum_choices` uses one of the four choice builders defined in `django_enum_choices.choice_builders`, named `value_value`.

It returns a tuple containing the enumeration's value twice:

```python
from django_enum_choices.choice_builders import value_value

class MyEnum(Enum):
    A = 'a'
    B = 'b'

print(value_value(MyEnum.A))  # ('a', 'a')
```

You can use one of the four default ones that fits your needs:

* `value_value`
* `attribute_value`
* `value_attribute`
* `attribute_attribute`

For example:

```python
from django_enum_choices.choice_builders import attribute_value

class MyEnum(Enum):
    A = 'a'
    B = 'b'

class CustomReadableValueEnumModel(models.Model):
    enumerated_field = EnumChoiceField(
        MyEnum,
        choice_builder=attribute_value
    )
```

The resulting choices for `enumerated_field` will be `(('A', 'a'), ('B', 'b'))`

You can also define your own choice builder:

```python
class MyEnum(Enum):
    A = 'a'
    B = 'b'

def choice_builder(choice: Enum) -> Tuple[str, str]:
    return choice.value, choice.value.upper() + choice.value

class CustomReadableValueEnumModel(models.Model):
    enumerated_field = EnumChoiceField(
        MyEnum,
        choice_builder=choice_builder
    )
```

Which will result in the following choices `(('a', 'Aa'), ('b', 'Bb'))`

The values in the returned from `choice_builder` tuple will be cast to strings before being used.

## Changing/Removing options from enumerations
At any given point of time all instances of a model that has `EnumChoiceField` must have a value that is currently present in the enumeration.
When changing or removing an option from the enumeration, a custom database migration must be made prior to the enumeration change.

### Changing options
When chaging options we'll need several operations:

1. Inserting a new option with the new value that we want
2. Migrating all instances from the old option to the new one
3. Removing the old option and renaming the old one
4. Removing the custom data migration code, so migrations can be run on a clean database without an `AttributeError` ocurring

Example:

Initial setup:

```python
class MyEnum(Enum):
    A = 'a'
    B = 'b'

# Desired change:
# A = 'a_updated'

class MyModel(models.Model):
    enumerated_field = EnumChoiceField(MyEnum)
```

1. Insert a new option with the desired new value:
```python
class MyEnum:
    A_UPDATED = 'a_updated'
    A = 'a'
    B = 'b'
```
```bash
python manage.py makemigrations
```

2. Migrate model instances
```bash
python manage.py makemigrations app_label --empty
```
```python
# migration_name.py

def forwards(apps, schema_editor):
    MyModel = apps.get_model('app_label', 'MyModel')

    MyModel.objects.filter(enumerated_field=MyEnum.A).update(enumerated_field=MyEnum.A_UPDATED)

class Migration(migrations.Migration):
    ...

    operations = [
        migrations.RunPython(forwards),
    ]
```
```bash
python manage.py migrate
```

3. Remove old option and rename new one
```python
class MyEnum:
    A = 'a_updated'
    B = 'b'
```
```bash
python manage.py makemigrations
python manage.py migrate
```

4. Remove custom data migration code
```python
# migration_name.py

def forwards(apps, schema_editor):
	pass

class Migration(migrations.Migration):
    ...

    operations = [
        migrations.RunPython(forwards),
    ]
```

### Removing options
Removing options from the enumeration includes several operations as well:

1. Optional: Making the field nullable (if we want our existing instances' values to be `None`)
2. Migrating all instances to a new option (or None)
3. Removing the option from the enumeration
4. Removing the custom data migration code, so migrations can be run on a clean database without an `AttributeError` ocurring

Example:

Initial setup:

```python
class MyEnum(Enum):
    A = 'a'
    B = 'b'

# Desired change:
# class MyEnum(Enum):
#     A = 'a'

class MyModel(models.Model):
    enumerated_field = EnumChoiceField(MyEnum)
```

1. Optional: Make the field nullable (if you want your existing instances to have a `None` value)
```python
class MyModel(models.Model):
    enumerated_field = EnumChoiceField(MyEnum, blank=True, null=True)
```
```bash
python manage.py makemigrations
```

2. Migrate model instances
```bash
python manage.py makemigrations app_label --empty
```
```python
# migration_name.py

def forwards(apps, schema_editor):
    MyModel = apps.get_model('app_label', 'MyModel')

    MyModel.objects.filter(enumerated_field=MyEnum.B).update(enumerated_field=MyEnum.A)
	# OR MyModel.objects.filter(enumerated_field=MyEnum.B).update(enumerated_field=None)

class Migration(migrations.Migration):
    ...

    operations = [
        migrations.RunPython(forwards),
    ]
```
```bash
python manage.py migrate
```

3. Remove old option
```python
class MyEnum:
    A = 'a
```
```bash
python manage.py makemigrations
python manage.py migrate
```

4. Remove custom data migration code
```python
# migration_name.py

def forwards(apps, schema_editor):
	pass

class Migration(migrations.Migration):
    ...

    operations = [
        migrations.RunPython(forwards),
    ]
```


## Usage in the admin panel

Model fields, defined as `EnumChoiceField` can be used with almost all of the admin panel's
standard functionallities.

One exception from this their usage in `list_filter`.

If you need an `EnumChoiceField` inside a `ModelAdmin`'s `list_filter`, you can use the following
options:

* Define the entry insite the list filter as a tuple, containing the field's name and `django_enum_choices.admin.EnumChoiceListFilter`

```python
from django.contrib import admin

from django_enum_choices.admin import EnumChoiceListFilter

from .models import MyModel

@admin.register(MyModel)
class MyModelAdmin(admin.ModelAdmin):
    list_filter = [('enumerated_field', EnumChoiceListFilter)]
```

* Set `DJANGO_ENUM_CHOICES_REGISTER_LIST_FILTER` inside your settings to `True`, which will automatically set the `EnumChoiceListFilter` class to all
`list_filter` fields that are instances of `EnumChoiceField`. This way, they can be declared directly in the `list_filter` iterable:

```python
from django.contrib import admin

from .models import MyModel

@admin.register(MyModel)
class MyModelAdmin(admin.ModelAdmin):
    list_filter = ('enumerated_field', )
```


## Usage with forms

There are 2 rules of thumb:

1. If you use a `ModelForm`, everything will be taken care of automatically.
2. If you use a `Form`, you need to take into account what `Enum` and `choice_builder` you are using.


### Usage with `django.forms.ModelForm`

```python
from .models import MyModel

class ModelEnumForm(forms.ModelForm):
    class Meta:
        model = MyModel
        fields = ['enumerated_field']

form = ModelEnumForm({
    'enumerated_field': 'a'
})

form.is_valid()

print(form.save(commit=True))  # <MyModel: MyModel object (12)>
```

### Usage with `django.forms.Form`

If you are using the default `value_value` choice builder, you can just do that:

```python
from django_enum_choices.forms import EnumChoiceField

from .enumerations import MyEnum

class StandardEnumForm(forms.Form):
    enumerated_field = EnumChoiceField(MyEnum)

form = StandardEnumForm({
    'enumerated_field': 'a'
})
form.is_valid()

print(form.cleaned_data)  # {'enumerated_field': <MyEnum.A: 'a'>}
```

If you are passing a different choice builder, you have to also pass it to the form field:

```python
from .enumerations import MyEnum

def custom_choice_builder(choice):
    return 'Custom_' + choice.value, choice.value

class CustomChoiceBuilderEnumForm(forms.Form):
    enumerated_field = EnumChoiceField(
        MyEnum,
        choice_builder=custom_choice_builder
    )

form = CustomChoiceBuilderEnumForm({
    'enumerated_field': 'Custom_a'
})

form.is_valid()

print(form.cleaned_data)  # {'enumerated_field': <MyEnum.A: 'a'>}
```

## Usage with `django-filter`

As with forms, there are 2 general rules of thumb:

1. If you have declared an `EnumChoiceField` in the `Meta.fields` for a given `Meta.model`, you need to inherit `EnumChoiceFilterMixin` in your filter class & everything will be taken care of automatically.
2. If you are declaring an explicit field, without a model, you need to specify the `Enum` class & the `choice_builder`, if a custom one is used.

### By using a `Meta` inner class and inheriting from `EnumChoiceFilterMixin`

```python
import django_filters as filters

from django_enum_choices.filters import EnumChoiceFilterMixin

class ImplicitFilterSet(EnumChoiceFilterSetMixin, filters.FilterSet):
    class Meta:
        model = MyModel
        fields = ['enumerated_field']

filters = {
    'enumerated_field': 'a'
}
filterset = ImplicitFilterSet(filters)

print(filterset.qs.values_list('enumerated_field', flat=True))
# <QuerySet [<MyEnum.A: 'a'>, <MyEnum.A: 'a'>, <MyEnum.A: 'a'>]>
```

The `choice_builder` argument can be passed to `django_enum_choices.filters.EnumChoiceFilter` as well when using the field explicitly. When using `EnumChoiceFilterSetMixin`, the `choice_builder` is determined from the model field, for the fields defined inside the `Meta` inner class.

```python
import django_filters as filters

from django_enum_choices.filters import EnumChoiceFilter

def custom_choice_builder(choice):
    return 'Custom_' + choice.value, choice.value

class ExplicitCustomChoiceBuilderFilterSet(filters.FilterSet):
    enumerated_field = EnumChoiceFilter(
        MyEnum,
        choice_builder=custom_choice_builder
    )

filters = {
    'enumerated_field': 'Custom_a'
}
filterset = ExplicitCustomChoiceBuilderFilterSet(filters, MyModel.objects.all())

print(filterset.qs.values_list('enumerated_field', flat=True))  # <QuerySet [<MyEnum.A: 'a'>, <MyEnum.A: 'a'>, <MyEnum.A: 'a'>]>
```


### By declaring the field explicitly on the `FilterSet`

```python
import django_filters as filters

from django_enum_choices.filters import EnumChoiceFilter

class ExplicitFilterSet(filters.FilterSet):
    enumerated_field = EnumChoiceFilter(MyEnum)


filters = {
    'enumerated_field': 'a'
}
filterset = ExplicitFilterSet(filters, MyModel.objects.all())

print(filterset.qs.values_list('enumerated_field', flat=True))  # <QuerySet [<MyEnum.A: 'a'>, <MyEnum.A: 'a'>, <MyEnum.A: 'a'>]>
```

## Postgres ArrayField Usage

You can use `EnumChoiceField` as a child field of an Postgres `ArrayField`.

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

As with forms & filters, there are 2 general rules of thumb:

1. If you are using a `ModelSerializer` and you inherit `EnumChoiceModelSerializerMixin`, everything will be taken care of automatically.
2. If you are using a `Serializer`, you need to take the `Enum` class & `choice_builder` into acount.

### Using `serializers.ModelSerializer` with `EnumChoiceModelSerializerMixin`

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

When using the `EnumChoiceModelSerializerMixin` with DRF's `serializers.ModelSerializer`, the `choice_builder` is automatically passed from the model field to the serializer field.

### Using `serializers.ModelSerializer` without `EnumChoiceModelSerializerMixin`

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

If you are using a custom `choice_builder`, you need to pass that too.

```python
def custom_choice_builder(choice):
    return 'Custom_' + choice.value, choice.value

class CustomChoiceBuilderSerializer(serializers.Serializer):
    enumerted_field = EnumChoiceField(
        MyEnum,
        choice_builder=custom_choice_builder
    )

serializer = CustomChoiceBuilderSerializer({
    'enumerated_field': MyEnum.A
})

data = serializer.data # {'enumerated_field': 'Custom_a'}
```

### Using a subclass of `serializers.Serializer`

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

If you are using a custom `choice_builder`, you need to pass that too.

### Serializing PostgreSQL ArrayField

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

## Implementation details

* `EnumChoiceField` is a subclass of `CharField`.
* Only subclasses of `Enum` are valid arguments for `EnumChoiceField`.
* `max_length`, if passed, is ignored. `max_length` is automatically calculated from the longest choice.
* `choices` are generated using a special `choice_builder` function, which accepts an enumeration and returns a tuple of 2 items.
  * Four choice builder functions are defined inside `django_enum_choices.choice_builders`
  * By default the `value_value` choice builder is used. It produces the choices from the values in the enumeration class, like `(enumeration.value, enumeration.value)`
  * `choice_builder` can be overriden by passing a callable to the `choice_builder` keyword argument of `EnumChoiceField`.
  * All values returned from the choice builder **will be cast to strings** when generating choices.

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

	# The default choice builder `value_value` is being used

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

**Fork the repository**
```bash
git clone https://github.com/your-user-name/django-enum-choices.git django-enum-choices-yourname
cd django-enum-choices-yourname
git remote add upstream https://github.com/HackSoftware/django-enum-choices.git
```

Install the requirements:
```bash
pip install -e .[dev]
```

Linting and running the tests:
```bash
tox
```
