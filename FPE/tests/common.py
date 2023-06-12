import pathlib
import os

from core.handler import Handler


def json_file_source(source_file: str) -> str:
    return str(pathlib.Path.cwd() / "FPE" / "tests" / "json" / source_file)


def create_test_file(source_path: pathlib.Path) -> None:
    if not source_path.parent.exists():
        Handler.create_path(source_path.parent)
    with open(source_path, 'wb') as test_file:
        test_file.write(os.urandom(1024 * 1024))
