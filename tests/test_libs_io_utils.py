import io
import pathlib
import sys
import tempfile
import unittest

from cl_sii.libs.io_utils import with_encoding_utf8, with_mode_binary, with_mode_text  # noqa: F401


class FunctionsTest(unittest.TestCase):
    def test_with_encoding_utf8(self):
        filename = pathlib.Path(__file__).with_name('test_libs_io_utils-test-file-1.tmp')
        filename.touch()

        # Binary mode

        with open(str(filename), mode='rb') as f:
            self.assertTrue(isinstance(f, io.BufferedReader))
            with self.assertRaises(TypeError):
                with_encoding_utf8(f)

        with open(str(filename), mode='wb') as f:
            self.assertTrue(isinstance(f, io.BufferedWriter))
            with self.assertRaises(TypeError):
                with_encoding_utf8(f)

        with open(str(filename), mode='w+b') as f:
            self.assertTrue(isinstance(f, io.BufferedRandom))
            with self.assertRaises(TypeError):
                with_encoding_utf8(f)

        with io.BytesIO() as f:
            self.assertTrue(isinstance(f, io.BytesIO))
            with self.assertRaises(TypeError):
                with_encoding_utf8(f)

        with tempfile.NamedTemporaryFile() as f:
            self.assertTrue(isinstance(f, tempfile._TemporaryFileWrapper))
            with self.assertRaises(TypeError):
                with_encoding_utf8(f)

        with tempfile.SpooledTemporaryFile() as f:
            self.assertTrue(isinstance(f, tempfile.SpooledTemporaryFile))
            with self.assertRaises(TypeError):
                with_encoding_utf8(f)

        # Text mode - encoding 'utf-8'

        with open(str(filename), mode='rt', encoding='utf-8') as f:
            self.assertTrue(isinstance(f, io.TextIOWrapper))
            self.assertTrue(with_encoding_utf8(f))

        with open(str(filename), mode='wt', encoding='utf-8') as f:
            self.assertTrue(isinstance(f, io.TextIOWrapper))
            self.assertTrue(with_encoding_utf8(f))

        with open(str(filename), mode='w+t', encoding='utf-8') as f:
            self.assertTrue(isinstance(f, io.TextIOWrapper))
            self.assertTrue(with_encoding_utf8(f))

        with io.StringIO() as f:
            # note: has no encoding
            self.assertTrue(isinstance(f, io.StringIO))
            self.assertTrue(with_encoding_utf8(f))

        with tempfile.NamedTemporaryFile(mode='rt', encoding='utf-8') as f:
            self.assertTrue(isinstance(f, tempfile._TemporaryFileWrapper))
            self.assertTrue(with_encoding_utf8(f))

        with tempfile.SpooledTemporaryFile(mode='rt', encoding='utf-8') as f:
            self.assertTrue(isinstance(f, tempfile.SpooledTemporaryFile))
            if sys.version_info[:3] >= (3, 7, 6):
                self.assertTrue(with_encoding_utf8(f))
            else:
                # note: this is a strange case (Python 3.7).
                self.assertFalse(with_encoding_utf8(f))

        # Text mode - encoding 'latin1'

        with open(str(filename), mode='rt', encoding='latin1') as f:
            self.assertTrue(isinstance(f, io.TextIOWrapper))
            self.assertFalse(with_encoding_utf8(f))

        with open(str(filename), mode='wt', encoding='latin1') as f:
            self.assertTrue(isinstance(f, io.TextIOWrapper))
            self.assertFalse(with_encoding_utf8(f))

        with open(str(filename), mode='w+t', encoding='latin1') as f:
            self.assertTrue(isinstance(f, io.TextIOWrapper))
            self.assertFalse(with_encoding_utf8(f))

        with tempfile.NamedTemporaryFile(mode='rt', encoding='latin1') as f:
            self.assertTrue(isinstance(f, tempfile._TemporaryFileWrapper))
            self.assertFalse(with_encoding_utf8(f))

        with tempfile.SpooledTemporaryFile(mode='rt', encoding='latin1') as f:
            self.assertTrue(isinstance(f, tempfile.SpooledTemporaryFile))
            self.assertFalse(with_encoding_utf8(f))

        filename.unlink()

    def test_with_mode_x(self):
        # For the sake of simplicity test here both 'with_mode_binary' and 'with_mode_text'.

        filename = pathlib.Path(__file__).with_name('test_libs_io_utils-test-file-2.tmp')
        filename.touch()

        # Binary mode

        with open(str(filename), mode='rb') as f:
            self.assertTrue(isinstance(f, io.BufferedReader))
            self.assertTrue(with_mode_binary(f))
            self.assertFalse(with_mode_text(f))

        with open(str(filename), mode='wb') as f:
            self.assertTrue(isinstance(f, io.BufferedWriter))
            self.assertTrue(with_mode_binary(f))
            self.assertFalse(with_mode_text(f))

        with open(str(filename), mode='w+b') as f:
            self.assertTrue(isinstance(f, io.BufferedRandom))
            self.assertTrue(with_mode_binary(f))
            self.assertFalse(with_mode_text(f))

        with io.BytesIO() as f:
            self.assertTrue(isinstance(f, io.BytesIO))
            self.assertTrue(with_mode_binary(f))
            self.assertFalse(with_mode_text(f))

        with tempfile.NamedTemporaryFile() as f:

            self.assertTrue(isinstance(f, tempfile._TemporaryFileWrapper))
            self.assertTrue(with_mode_binary(f))
            self.assertFalse(with_mode_text(f))

        with tempfile.SpooledTemporaryFile() as f:
            self.assertTrue(isinstance(f, tempfile.SpooledTemporaryFile))
            self.assertTrue(with_mode_binary(f))
            self.assertFalse(with_mode_text(f))

        # Text mode

        with open(str(filename), mode='rt') as f:
            self.assertTrue(isinstance(f, io.TextIOWrapper))
            self.assertFalse(with_mode_binary(f))
            self.assertTrue(with_mode_text(f))

        with open(str(filename), mode='wt') as f:
            self.assertTrue(isinstance(f, io.TextIOWrapper))
            self.assertFalse(with_mode_binary(f))
            self.assertTrue(with_mode_text(f))

        with open(str(filename), mode='w+t') as f:
            self.assertTrue(isinstance(f, io.TextIOWrapper))
            self.assertFalse(with_mode_binary(f))
            self.assertTrue(with_mode_text(f))

        with io.StringIO() as f:
            self.assertTrue(isinstance(f, io.StringIO))
            self.assertFalse(with_mode_binary(f))
            self.assertTrue(with_mode_text(f))

        with tempfile.NamedTemporaryFile(mode='rt') as f:
            self.assertTrue(isinstance(f, tempfile._TemporaryFileWrapper))
            self.assertFalse(with_mode_binary(f))
            self.assertTrue(with_mode_text(f))

        with tempfile.SpooledTemporaryFile(mode='rt') as f:
            self.assertTrue(isinstance(f, tempfile.SpooledTemporaryFile))
            self.assertFalse(with_mode_binary(f))
            self.assertTrue(with_mode_text(f))

        filename.unlink()
