import pytest
import os

from core.arguments import Arguments, ArgumentsError


class TestCoreArguments:

    def test_arguments_with_existing_json_file(self):
        arg = Arguments(
            [os.path.join(os.getcwd(), "FPE", "tests", "json", "test_valid.json")])
        assert arg.file == os.path.join(
            os.getcwd(), "FPE", "tests", "json", "test_valid.json")

    def test_arguments_with_nonexistant_json__file(self):
        with pytest.raises(ArgumentsError):
            _ = Arguments(
                [os.path.join(os.getcwd(), "FPE", "tests", "json", "test.jsn")])

    def test_arguments_output_of_help(self, capsys):
        with pytest.raises(SystemExit):
            _ = Arguments(["-h"])
        out, _ = capsys.readouterr()
        assert out.startswith("usage")