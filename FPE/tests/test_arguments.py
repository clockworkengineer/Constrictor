from pytest import raises
import os

from core.arguments import Arguments, ArgumentsError

class TestArguments:
    
    def test_arguments_with_existing_json_file(self):
        arg = Arguments([os.path.join(os.getcwd(), "FPE","tests","test.json")])
        assert arg.file == os.path.join(os.getcwd(), "FPE", "tests","test.json")


    def test_arguments_with_nonexistant_json__file(self):
        with raises(ArgumentsError):
            _ = Arguments([os.path.join(os.getcwd(), "FPE", "tests", "test.jsn")])


    def test_arguments_output_of_help(self, capsys):
        with raises(SystemExit):
            _ = Arguments(["-h"])
        out, _ = capsys.readouterr()
        assert out == 'usage: __main__.py [-h] file\n\nProcess files copied into watch folder with a custom handler(s).\n\npositional arguments:\n  file        Configuration file\n\noptional arguments:\n  -h, --help  show this help message and exit\n'
