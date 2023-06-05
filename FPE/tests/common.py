import pathlib
import os


def json_file_source(source_file: str) -> str:
    return str(pathlib.Path.cwd() / "FPE" / "tests" / "json" / source_file)


def create_test_file(source_path: pathlib.Path) -> None:
    with open(source_path, 'wb') as test_file:
        test_file.write(os.urandom(1024 * 1024))
