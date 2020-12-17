from enum import Enum
from typing import Tuple, Type

from django.db.models import CharField
from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator
from django.utils.translation import gettext as _
from django.utils.text import capfirst

from .exceptions import EnumChoiceFieldException
from .validators import EnumValueMaxLengthValidator
from .choice_builders import value_value
from .utils import as_choice_builder, value_from_built_choice, build_enum_choices
from .forms import EnumChoiceField as EnumChoiceFormField


class EnumChoiceField(CharField):
    description = _('EnumChoiceField for %(enum_class)')

    def __init__(self, enum_class: Type[Enum], choice_builder=value_value, **kwargs):
        if not issubclass(enum_class, Enum):
            raise EnumChoiceFieldException(
                _('`enum_class` argument must be a child of `Enum`')
            )

        self.enum_class = enum_class
        self.choice_builder = self._get_choice_builder(choice_builder)

        # Saving original for proper deconstruction
        self._original_choice_builder = choice_builder

        built_choices = self.build_choices()

        # `choices` is passed to `__init__` when migrations are generated
        # `choices` should not be passed when normally initializing the field
        self._passed_choices = kwargs.get(
            'choices',
            built_choices
        )  # Saved for deconstruction

        kwargs['choices'] = built_choices

        calculated_max_length = self._calculate_max_length(**kwargs)

        kwargs.setdefault('max_length', calculated_max_length)

        super().__init__(**kwargs)

        # Removing `MaxLengthValidator` instances and adding
        # an `EnumValueMaxLengthValidator` instance
        self.validators = [
            validator for validator in self.validators
            if not isinstance(validator, MaxLengthValidator)
        ]

        self.validators.append(
            EnumValueMaxLengthValidator(
                value_builder=self.get_prep_value,
                limit_value=kwargs['max_length']
            )
        )

    def _get_choice_builder(self, choice_builder):
        if not callable(choice_builder):
            raise EnumChoiceFieldException(
                _('`{}.choice_builder` must be a callable.'.format(
                    self.enum_class.__name__
                ))
            )

        return as_choice_builder(choice_builder)

    def build_choices(self) -> Tuple[Tuple[str]]:
        return build_enum_choices(
            self.enum_class,
            self.choice_builder
        )

    def _calculate_max_length(self, **kwargs) -> int:
        max_choice_length = max(len(choice) for choice, _ in kwargs['choices'])

        return max_choice_length

    def to_enum_value(self, value):
        if value is None:
            return

        for choice in self.enum_class:
            # Check if the value from the built choice matches the passed one
            if value_from_built_choice(self.choice_builder(choice)) == value:
                return choice

        raise ValidationError(
            _('Value {} not found in {}'.format(value, self.enum_class))
        )

    def get_prep_value(self, value):
        return value_from_built_choice(
            self.choice_builder(value)
        )

    def from_db_value(self, value, expression, connection, *args):
        # Accepting `*args` because Django 1.11 calls with an extra
        # `context` argument

        return self.to_enum_value(value)

    def to_python(self, value):
        if isinstance(value, self.enum_class):
            return value

        return self.to_enum_value(value)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()

        kwargs['choices'] = self._passed_choices

        if self.enum_class:
            kwargs['enum_class'] = self.enum_class

        if self.choice_builder:
            kwargs['choice_builder'] = self._original_choice_builder

        return name, path, args, kwargs

    def validate(self, value, *args, **kwargs):
        """
        Runs standard `django.db.models.Field` validation
        with different logic for choices validation
        """

        if not self.editable:
            return

        if value is None and not self.null:
            raise ValidationError(self.error_messages['null'], code='null')

        if not self.blank and value in self.empty_values:
            raise ValidationError(self.error_messages['blank'], code='blank')

        enum_value = value

        if not isinstance(enum_value, self.enum_class):
            try:
                enum_value = self.to_enum_value(value)

                if enum_value not in self.enum_class:
                    raise ValidationError(
                        self.error_messages['invalid_choice'],
                        code='invalid_choice',
                        params={'value': value}
                    )
            except ValidationError:
                raise ValidationError(
                    self.error_messages['invalid_choice'],
                    code='invalid_choice',
                    params={'value': value}
                )

    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        return self.get_prep_value(value)

    @property
    def flatchoices(self):
        """
        Django admin uses `flatchoices` to generate a value under the
        fields column in their list display. By default it calculates
        `flatchoices` as a Tuple[Tuple[str]],
        I.E: `(('choice1', 'choice1'), ('choice2', 'choice2'))
        It accesses the readable value by using the actual value
        which is an enumeration instance in our case.
        Since that does not match inside the original `flatchoices`
        it sets the display value to `-`.
        """

        flatchoices = super()._get_flatchoices()

        return [
            (self.to_enum_value(choice), readable)
            for choice, readable in flatchoices
        ]

    def formfield(self, **kwargs):
        """
        Uses `django.forms.Field`'s parameter generation with
        `EnumChoiceField` specific updates.
        """

        defaults = {
            'required': not self.blank,
            'label': capfirst(self.verbose_name),
            'help_text': self.help_text,
            'enum_class': self.enum_class,
            'choice_builder': self.choice_builder
        }

        if self.has_default():
            if callable(self.default):
                defaults['initial'] = self.default
                defaults['show_hidden_initial'] = True
            else:
                defaults['initial'] = self.get_default()

        include_blank = (self.blank or
                         not (self.has_default() or 'initial' in kwargs))
        defaults['choices'] = self.get_choices(include_blank=include_blank)

        # Many of the subclass-specific formfield arguments (min_value,
        # max_value) don't apply for choice fields, so be sure to only pass
        # the values that TypedChoiceField will understand.
        for k in list(kwargs):
            if k not in (
                'coerce', 'choices', 'required', 'enum_class', 'disabled',
                'choice_builder, ''widget', 'label', 'initial', 'help_text',
                'error_messages', 'show_hidden_initial',
            ):
                del kwargs[k]

        defaults.update(kwargs)

        return EnumChoiceFormField(**defaults)
