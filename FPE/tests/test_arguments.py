from core.arguments import Arguments, ArgumentsError
from pytest import raises


def test_arguments_with_existing_json_file():
    arg = Arguments(["C:\\Projects\\Constrictor\\FPE\\fpe.json"])
    assert (arg.file == "C:\\Projects\\Constrictor\\FPE\\fpe.json")


def test_arguments_with_nonexistant_json__file():
    with raises(ArgumentsError):
        _ = Arguments(["C:\\Projects\\Constrictor\\FPE\\fpee.json"])
