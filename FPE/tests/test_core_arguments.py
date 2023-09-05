import pytest

from tests.common import json_file_source
from core.arguments import Arguments, ArgumentsError


class TestCoreArguments:
    def test_arguments_with_existing_json_file(self) -> None:
        config_file = json_file_source("test_valid.json")
        arg = Arguments([config_file])
        assert arg.file == config_file

    def test_arguments_with_nonexistant_json__file(self) -> None:
        with pytest.raises(ArgumentsError):
            _ = Arguments([json_file_source("test.jsn")])

    def test_arguments_output_of_help(self, capsys) -> None:
        with pytest.raises(SystemExit):
            _ = Arguments(["-h"])
        out, _ = capsys.readouterr()
        assert out.startswith("usage")
