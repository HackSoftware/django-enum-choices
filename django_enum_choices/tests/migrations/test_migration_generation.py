from enum import Enum
from typing import List

from django.conf import settings
from django.test import TestCase, TransactionTestCase, override_settings
from django.db import models, connections
from django.db.migrations.migration import Migration
from django.db.migrations.autodetector import MigrationAutodetector
from django.db.migrations.state import ModelState, ProjectState

from django_enum_choices.fields import EnumChoiceField


class MigrationTestMixin:
    def _create_initial_enum_class(self):
        class CustomEnum(Enum):
            FIRST = 'first'
            SECOND = 'second'

        return CustomEnum

    def _create_secondary_enum_class(self):
        class CustomEnum(Enum):
            FIRST = 'first'
            SECOND = 'second'
            EXTRA_LONG_ENUMERATION = 'extra long enumeration'

        return CustomEnum

    def make_project_state(self, model_states: List[ModelState]) -> ProjectState:
        project_state = ProjectState()

        for model_state in model_states:
            project_state.add_model(model_state.clone())

        return project_state

    def get_changes(self, app_label: str, initial: ProjectState, after: ProjectState) -> List[Migration]:
        return MigrationAutodetector(
            initial,
            after
        )._detect_changes().get(app_label, [])

    def setUp(self):
        self.initial_model_state = ModelState(
            'migrations_testapp', '_CustomModel', [
                ('id', models.AutoField(primary_key=True)),
                ('enumeration', EnumChoiceField(self._create_initial_enum_class()))
            ]
        )

        self.secondary_model_state = ModelState(
            'migrations_testapp', '_CustomModel', [
                ('id', models.AutoField(primary_key=True)),
                ('enumeration', EnumChoiceField(self._create_secondary_enum_class()))
            ]
        )


class MigrationGenerationTests(MigrationTestMixin, TestCase):
    def test_migration_changes(self):
        initial = self.make_project_state([self.initial_model_state])
        after = self.make_project_state([self.secondary_model_state])

        changes = self.get_changes('migrations_testapp', initial, after)

        self.assertEqual(len(changes), 1)

        operations = changes[0].operations

        self.assertEqual(len(operations), 1)

        operation = operations[0]
        *_, deconstruction_kwargs = operation.field.deconstruct()

        self.assertEqual(
            deconstruction_kwargs.get('max_length', 0),
            len(self._create_secondary_enum_class().EXTRA_LONG_ENUMERATION.value)
        )
        self.assertEqual(
            deconstruction_kwargs.get('choices', []),
            [
                ('first', 'first'),
                ('second', 'second'),
                ('extra long enumeration', 'extra long enumeration')
            ]
        )


class MigrationExecutionTestMixin(MigrationTestMixin):
    databases = ['default']

    def assertColumnType(self, table, column, column_size):
        using = settings.CURRENT_DATABASE

        with connections[using].cursor() as cursor:
            introspection = connections[using].introspection

            # Django < 2.2 PG database backend compatibillity
            try:
                table_description = introspection.get_table_description(
                    cursor, table
                )
            except TypeError:
                table_description = cursor.description

            column = [
                col for col in table_description if col.name == column
            ]

            if not column:
                assert False, 'Column {} not found in {}'.format(column, table)

            column = column[0]

            field_type = introspection.data_types_reverse[column.type_code]

            # Django < 2.2 sqlite3 backend compatibillity
            if isinstance(field_type, tuple):
                field_type = field_type[0]

            internal_size = column.internal_size

            self.assertEqual(field_type, 'CharField')
            self.assertEqual(internal_size, column_size)

    def test_migration_is_applied(self):
        initial = self.make_project_state([self.initial_model_state])
        after = self.make_project_state([self.secondary_model_state])

        initial_migration = self.get_changes('migrations_testapp', ProjectState(), initial)[0]

        with connections[settings.CURRENT_DATABASE].schema_editor() as schema_editor:
            applied_initial_state = initial_migration.apply(
                ProjectState(),
                schema_editor
            ).clone()

        self.assertColumnType(
            'migrations_testapp__custommodel',
            'enumeration',
            6
        )

        after_migration = self.get_changes('migrations_testapp', applied_initial_state, after)[0]

        with connections[settings.CURRENT_DATABASE].schema_editor() as schema_editor:
            after_migration.apply(initial, schema_editor)

        self.assertColumnType(
            'migrations_testapp__custommodel',
            'enumeration',
            len(self._create_secondary_enum_class().EXTRA_LONG_ENUMERATION.value),
        )


class MigrationExecutionSQLite3Tests(MigrationExecutionTestMixin, TransactionTestCase):
    database = ['default']


@override_settings(CURRENT_DATABASE='postgresql')
class MigrationExecutionPostgreSQLTests(MigrationExecutionTestMixin, TransactionTestCase):
    databases = ['postgresql']


@override_settings(CURRENT_DATABASE='mysql')
class MigrationExecutionMySQLTests(MigrationExecutionTestMixin, TransactionTestCase):
    databases = ['mysql']
