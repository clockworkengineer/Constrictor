from core.arguments import Arguments, ArgumentsError
from pytest import raises
import os


def test_arguments_with_existing_json_file():
    arg = Arguments([os.path.join(os.getcwd(), "FPE\\tests\\test.json")])
    assert arg.file == os.path.join(os.getcwd(), "FPE\\tests\\test.json")


def test_arguments_with_nonexistant_json__file():
    with raises(ArgumentsError):
        _ = Arguments([os.path.join(os.getcwd(), "FPE\\tests\\test.jsn")])
