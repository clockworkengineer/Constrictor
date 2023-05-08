import pytest
import pathlib

from core.arguments import Arguments, ArgumentsError


@pytest.fixture()
def json_file_source():
    yield pathlib.Path.cwd() / "FPE" / "tests" / "json"


class TestCoreArguments:

    def test_arguments_with_existing_json_file(self, json_file_source):
        config_file = str(json_file_source / "test_valid.json")
        arg = Arguments([config_file])
        assert arg.file == config_file

    def test_arguments_with_nonexistant_json__file(self, json_file_source):
        with pytest.raises(ArgumentsError):
            _ = Arguments([str(json_file_source / "test.jsn")])

    def test_arguments_output_of_help(self, capsys):
        with pytest.raises(SystemExit):
            _ = Arguments(["-h"])
        out, _ = capsys.readouterr()
        assert out.startswith("usage")
