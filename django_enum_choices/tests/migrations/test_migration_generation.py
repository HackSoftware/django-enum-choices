from enum import Enum
from typing import List

from django.conf import settings
from django.test import TestCase, TransactionTestCase, override_settings
from django.db import models, connections
from django.db.migrations.migration import Migration
from django.db.migrations.autodetector import MigrationAutodetector
from django.db.migrations.state import ModelState, ProjectState

from django_enum_choices.fields import EnumChoiceField


class CustomEnum(Enum):
    FIRST = 'first'
    SECOND = 'second'


class MigrationTestMixin:
    def _create_initial_enum_class(self):
        return CustomEnum

    def _create_secondary_enum_class(self):
        global CustomEnum

        current_enum_names = CustomEnum._member_names_
        current_enum_map = CustomEnum._member_map_

        class Temp(Enum):
            EXTRA_LONG_ENUMERATION = 'extra long enumeration'

        CustomEnum._member_names_ = current_enum_names + Temp._member_names_
        CustomEnum._member_map_ = {**current_enum_map, **Temp._member_map_}

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

    def set_initial_model_state(self):
        self.initial_model_state = ModelState(
            'migrations_testapp', '_CustomModel', [
                ('id', models.AutoField(primary_key=True)),
                ('enumeration', EnumChoiceField(self._create_initial_enum_class()))
            ]
        )

    def set_secondary_model_state(self):
        self.secondary_model_state = ModelState(
            'migrations_testapp', '_CustomModel', [
                ('id', models.AutoField(primary_key=True)),
                ('enumeration', EnumChoiceField(self._create_secondary_enum_class()))
            ]
        )



class MigrationExecutionTestMixin(MigrationTestMixin):
    # databases = ['default']

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
        self.set_initial_model_state()
        initial = self.make_project_state([self.initial_model_state])

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

        self.set_secondary_model_state()
        initial = self.make_project_state([self.initial_model_state])
        after = self.make_project_state([self.secondary_model_state])
        after_migration = self.get_changes('migrations_testapp', applied_initial_state, after)[0]

        with connections[settings.CURRENT_DATABASE].schema_editor() as schema_editor:
            after_migration.apply(initial, schema_editor)


        self.assertColumnType(
            'migrations_testapp__custommodel',
            'enumeration',
            len(self._create_secondary_enum_class().EXTRA_LONG_ENUMERATION.value),
        )


# class MigrationExecutionSQLite3Tests(MigrationExecutionTestMixin, TransactionTestCase):
#     database = ['default']


@override_settings(CURRENT_DATABASE='default')
class MigrationExecutionPostgreSQLTests(MigrationExecutionTestMixin, TransactionTestCase):
    databases = ['default']


# @override_settings(CURRENT_DATABASE='mysql')
# class MigrationExecutionMySQLTests(MigrationExecutionTestMixin, TransactionTestCase):
#     databases = ['mysql']
