import os
import shutil
import subprocess
import shlex

import psycopg2
from psycopg2.extras import DictCursor


class Database:
    def __init__(self):
        self.open()

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
        self.connection = psycopg2.connect('postgres:///django_enum_choices_e2e')

    def close(self):
        self.connection.close()


class Setuper:
    def __init__(self):
        self.cwd = os.getcwd()

    def get_base_project_location(self):
        return f'{self.cwd}/e2e'

    def get_new_project_location(self):
        return f'{self.cwd}/e2e_testing'

    def get_models_path(self):
        return f'{self.get_new_project_location()}/test_models/models.py'

    def call(self, command):
        subprocess.call(shlex.split(command))

    def before_setup(self, database):
        database.close()

        self.call('dropdb --if-exists django_enum_choices_e2e')
        self.call('createdb -O radorado django_enum_choices_e2e')

        database.open()

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

        models_content = models_content.replace(' #', '')

        with open(models, 'w') as models_file:
            models_file.write(models_content)

        os.chdir(new_project_location)
        self.call('python manage.py makemigrations')
        self.call('python manage.py migrate')

    def after_setup(self):
        new_project_location = self.get_new_project_location()

        if os.path.exists(new_project_location):
            shutil.rmtree(new_project_location)


setuper = Setuper()
database = Database()

setuper.before_setup(database)

print(database.get_column_size())
print(setuper.get_base_project_location())
print(setuper.get_new_project_location())
print(setuper.get_models_path())

setuper.setup()

print(database.get_column_size())

setuper.after_setup()
