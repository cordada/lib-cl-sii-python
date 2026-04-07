import tempfile
import unittest

from cl_sii.libs.charset_utils import clean_unicode, detect_file_encoding


class FunctionsTest(unittest.TestCase):
    def test_clean_unicode(self) -> None:
        expected = 'É'
        self.assertEqual(clean_unicode('É'), expected)
        self.assertEqual(clean_unicode('\u00c9'), expected)
        self.assertEqual(clean_unicode('\u0045\u0301'), expected)
        self.assertEqual(clean_unicode('\N{LATIN CAPITAL LETTER E WITH ACUTE}'), expected)
        self.assertEqual(
            clean_unicode('\N{LATIN CAPITAL LETTER E}\N{COMBINING ACUTE ACCENT}'), expected
        )

    def test_clean_unicode_empty_string(self) -> None:
        empty_string = ''
        self.assertEqual(clean_unicode(empty_string), empty_string)

    def test_detect_encoding_utf8(self) -> None:
        content = 'Este es un texto en español con acentos y ñ'.encode('utf-8')
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
        self.assertEqual(detect_file_encoding(temp_file_path), 'utf-8')

    def test_detect_encoding_ascii(self) -> None:
        content = 'This is a simple ASCII text.'.encode('ascii')
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
        self.assertEqual(detect_file_encoding(temp_file_path), 'utf-8')

    def test_detect_encoding_default(self) -> None:
        """
        The file does not have a valid encoding
        so the default encoding should be returned
        """
        content = b'\x80\x81\x82\x83\x84\x85'
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
        self.assertEqual(detect_file_encoding(temp_file_path), 'utf-8')
