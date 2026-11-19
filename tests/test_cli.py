import importlib
import io
import sys
import unittest
from contextlib import redirect_stdout
from unittest import mock


class TestCLI(unittest.TestCase):
    def setUp(self):
        self.tqdm_patch = mock.patch.dict(sys.modules, {"tqdm": None})
        self.tqdm_patch.start()
        self.addCleanup(self.tqdm_patch.stop)

    def import_cli(self):
        return importlib.reload(importlib.import_module("speech_recognition.cli"))

    def test_import_without_tqdm(self):
        self.assertTrue(callable(self.import_cli().main))

    def test_help_without_tqdm(self):
        cli = self.import_cli()
        with redirect_stdout(io.StringIO()) as output:
            with self.assertRaises(SystemExit) as raised:
                cli.main(["--help"])
        self.assertEqual(raised.exception.code, 0)
        self.assertIn("usage: sprc", output.getvalue())

    def test_no_arguments_without_tqdm(self):
        cli = self.import_cli()
        with redirect_stdout(io.StringIO()) as output:
            cli.main([])
        self.assertIn("usage: sprc", output.getvalue())

    def test_download_help_without_tqdm(self):
        cli = self.import_cli()
        with redirect_stdout(io.StringIO()) as output:
            with self.assertRaises(SystemExit) as raised:
                cli.main(["download", "--help"])
        self.assertEqual(raised.exception.code, 0)
        self.assertIn("usage: sprc download", output.getvalue())


if __name__ == "__main__":
    unittest.main()
