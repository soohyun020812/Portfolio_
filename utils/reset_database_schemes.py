import json
import os
import pathlib
import shutil
import sys

import django
from django.core.management import call_command

db_path = pathlib.Path("db.sqlite3")


def reset_database_schemes(app_names):
    for app_name in app_names:
        migration_path = pathlib.Path(app_name, "migrations")
        if migration_path.exists():
            for item in migration_path.iterdir():
                # __init__.py 파일은 삭제하지 않음
                if item.name != "__init__.py":
                    if item.is_dir():
                        shutil.rmtree(item)  # 디렉토리 삭제
                    else:
                        item.unlink()  # 파일 삭제
                        print(f"{app_name}의 migration 파일 f{item}을 삭제했습니다.")

    if db_path.exists():
        db_path.unlink()
        db_path.touch()


def setup_django(project_name):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"{project_name}.settings")
    django.setup()


def make_and_apply_migrations(project_name):
    setup_django(project_name)  # project_name을 setup_django에 전달

    call_command("makemigrations")
    call_command("migrate")


if __name__ == "__main__":
    sys.path.append(os.getcwd())

    app_names = input("Enter app names separated by space: ").split()
    project_name = input("Enter project name: ")

    reset_database_schemes(app_names)
    make_and_apply_migrations(project_name)
