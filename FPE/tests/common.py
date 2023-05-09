import pathlib


def json_file_source(source_file: str) -> str:
    return str(pathlib.Path.cwd() / "FPE" / "tests" / "json" / source_file)