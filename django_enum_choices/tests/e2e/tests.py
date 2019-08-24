import os
import shutil
from subprocess import check_output
import shlex

import psycopg2
from psycopg2.extras import DictCursor


class Database:
    def get_column_size(self):
        cursor = self.connection.cursor(
            cursor_factory=DictCursor
        )

        query = """
        SELECT character_maximum_length AS max_length
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE table_name = 'test_models_somemodel' and column_name = 'choices'
        """

        cursor.execute(query)

        result = cursor.fetchone()

        return result['max_length']

    def open(self):
        database_url = os.environ.get('DATABASE_URL', 'postgres:///django_enum_choices_e2e')
        self.connection = psycopg2.connect(database_url)

    def close(self):
        self.connection.close()


class Setuper:
    def __init__(self, database, test_case):
        self.cwd = os.getcwd()
        self.database = database
        self.test_case = test_case

    def get_base_project_location(self):
        return f'{self.cwd}/e2e'

    def get_new_project_location(self):
        return f'{self.cwd}/e2e_testing'

    def get_models_path(self):
        return f'{self.get_new_project_location()}/test_models/models.py'

    def call(self, command):
        result = check_output(shlex.split(command)).decode('utf-8')

        return result

    def before_setup(self):
        if not os.environ.get('CI', False):
            self.call('dropdb --if-exists django_enum_choices_e2e')
            self.call('createdb django_enum_choices_e2e')

        self.database.open()

        base_project_location = self.get_base_project_location()

        os.chdir(base_project_location)
        self.call('python manage.py migrate')

    def setup(self):
        base_project_location = self.get_base_project_location()
        new_project_location = self.get_new_project_location()

        if os.path.exists(new_project_location):
            shutil.rmtree(new_project_location)

        shutil.copytree(
            src=base_project_location,
            dst=new_project_location
        )

        models = self.get_models_path()

        with open(models, 'r') as models_file:
            models_content = models_file.read()

        models_content = models_content.replace(f' #{self.test_case}', '')

        with open(models, 'w') as models_file:
            models_file.write(models_content)

    def after_setup(self):
        new_project_location = self.get_new_project_location()

        if os.path.exists(new_project_location):
            shutil.rmtree(new_project_location)

        os.chdir(self.cwd)
        self.database.close()


def test_case_1():
    """
    If we add new choice, which changes the max length, we should have a migration,
    plus the column in postgres should be affected.
    """
    print('Running test case 1')

    database = Database()

    setuper = Setuper(database, 'TEST_1')

    setuper.before_setup()
    assert database.get_column_size() == 3, 'Initial max length should be 3'

    setuper.setup()

    new_project_location = setuper.get_new_project_location()

    os.chdir(new_project_location)

    result = setuper.call('python manage.py makemigrations')

    assert 'No changes detected' not in result, 'There should be new migrations'

    print(result)

    print(setuper.call('python manage.py migrate'))

    assert database.get_column_size() == 4, 'Migration should increase the max length to 4'

    setuper.after_setup()


def test_case_2():
    """
    If we add new choice, but within the existing max length, we should have a new migration.
    """
    print('Running test case 2')

    database = Database()

    setuper = Setuper(database, 'TEST_2')
    setuper.before_setup()
    setuper.setup()

    new_project_location = setuper.get_new_project_location()

    os.chdir(new_project_location)

    result = setuper.call('python manage.py makemigrations')

    assert 'No changes detected' not in result, 'There should be new migrations'

    print(result)

    print(setuper.call('python manage.py migrate'))

    setuper.after_setup()


test_case_1()
test_case_2()
