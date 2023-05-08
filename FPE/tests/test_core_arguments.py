import pytest
import pathlib

from core.arguments import Arguments, ArgumentsError


class TestCoreArguments:

    def test_arguments_with_existing_json_file(self):
        config_file =  str(pathlib.Path.cwd() / "FPE" / "tests" / "json" / "test_valid.json")
        arg = Arguments([config_file])
        assert arg.file == config_file

    def test_arguments_with_nonexistant_json__file(self):
        with pytest.raises(ArgumentsError):
            _ = Arguments(
                 [str(pathlib.Path.cwd() / "FPE" / "tests" / "json" / "test.jsn")])

    def test_arguments_output_of_help(self, capsys):
        with pytest.raises(SystemExit):
            _ = Arguments(["-h"])
        out, _ = capsys.readouterr()
        assert out.startswith("usage")
