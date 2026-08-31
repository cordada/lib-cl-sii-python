import codecs
import tempfile
import unittest
from unittest import mock

from cl_sii.libs.charset_utils import clean_unicode, detect_encoding, detect_file_encoding


# Contents of a real file of "cesiones" of a period, retrieved from the SII, that used to make
# 'detect_file_encoding' return 'big5' and thus make the parsing fail with a 'UnicodeDecodeError'.
# The non-ASCII byte is in "N\xfdCLEO VIAL SPA".
_CESIONES_PERIODO_FILE_WITH_NON_ASCII_BYTES = (
    b'DATOS_CONSULTA; RUT=76653704-9;TIPO_CONSULTA=DEUDOR;DESDE_DDMMAAAA=24032025;'
    b'HASTA_DDMMAAAA=30032025\r\n'
    b'VENDEDOR;ESTADO_CESION;DEUDOR;MAIL_DEUDOR;TIPO_DOC;NOMBRE_DOC;FOLIO_DOC;'
    b'FCH_EMIS_DTE;MNT_TOTAL;CEDENTE;RZ_CEDENTE;MAIL_CEDENTE;CESIONARIO;'
    b'RZ_CESIONARIO;MAIL_CESIONARIO;FCH_CESION;MNT_CESION;FCH_VENCIMIENTO\r\n'
    b'77014473-6;Cesion Vigente;76653704-9;null;33;Factura Electronica;2227;'
    b'2025-03-24;7133883;77014473-6;N\xfdCLEO VIAL SPA;anavarro@nucleovial.cl;'
    b'76070625-6;Factoring Andes S.A;cbiava@factorandes.cl;'
    b'2025-03-24 19:23;7133883;2025-05-23\r\n'
    b'77014473-6;Cesion Vigente;76653704-9;null;33;Factura Electronica;2236;'
    b'2025-03-27;21041723;77014473-6;N\xfdCLEO VIAL SPA;svirtual@eurocapital.cl;'
    b'96861280-8;Eurocapital S.A.;infosv@eurocapital.cl;'
    b'2025-03-27 17:23;21041723;2025-05-26\r\n'
)


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
        The file does not match any known encoding, so an encoding that decodes any byte sequence
        should be returned.
        """
        content = b'\x80\x81\x82\x83\x84\x85'
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
        self.assertEqual(detect_file_encoding(temp_file_path), 'latin-1')

    def test_detect_encoding_of_empty_data(self) -> None:
        self.assertEqual(detect_encoding(b''), 'utf-8')

    def test_detect_encoding_of_ascii_data(self) -> None:
        self.assertEqual(detect_encoding(b'This is a simple ASCII text.'), 'utf-8')

    def test_detect_encoding_of_utf8_data(self) -> None:
        content = 'Este es un texto en español con acentos y ñ'.encode('utf-8')
        self.assertEqual(detect_encoding(content), 'utf-8')

    def test_detect_encoding_of_utf8_data_truncated_mid_character(self) -> None:
        """
        The data may be a sample of a larger file, cut in the middle of a multi-byte character.
        """
        content = ('Este es un texto en español con acentos y ñ' * 100).encode('utf-8')
        self.assertTrue(content.endswith(b'\xc3\xb1'))
        self.assertEqual(detect_encoding(content[:-1]), 'utf-8')

    def test_detect_encoding_of_legacy_8_bit_data(self) -> None:
        text = 'Cesión Vigente;MI CAÑOPITO SA;Factura Electrónica' * 20
        for encoding in ('iso-8859-1', 'cp1252'):
            with self.subTest(encoding=encoding):
                content = text.encode(encoding)
                detected_encoding = detect_encoding(content)
                self.assertEqual(content.decode(detected_encoding), text)

    def test_detect_encoding_of_data_with_bom(self) -> None:
        text = 'Cesión Vigente'
        for bom, encoding, expected_encoding in (
            (b'', 'utf-8-sig', 'utf-8-sig'),
            (b'', 'utf-16', 'utf-16'),
            (codecs.BOM_UTF16_LE, 'utf-16-le', 'utf-16'),
            (codecs.BOM_UTF16_BE, 'utf-16-be', 'utf-16'),
            (b'', 'utf-32', 'utf-32'),
        ):
            with self.subTest(encoding=encoding):
                content = bom + text.encode(encoding)
                self.assertEqual(detect_encoding(content), expected_encoding)
                self.assertEqual(content.decode(expected_encoding), text)

    def test_detect_encoding_of_data_with_a_few_non_ascii_bytes(self) -> None:
        """
        Regression test: this data used to be detected as 'big5', which can not decode it.
        """
        content = _CESIONES_PERIODO_FILE_WITH_NON_ASCII_BYTES
        detected_encoding = detect_encoding(content)
        # It must not raise.
        content.decode(detected_encoding)

    def test_detect_encoding_ignores_implausible_detected_encoding(self) -> None:
        """
        A multi-byte CJK encoding is always a false positive for this kind of data.
        """
        content = _CESIONES_PERIODO_FILE_WITH_NON_ASCII_BYTES
        with mock.patch(
            'cl_sii.libs.charset_utils.chardet.detect',
            return_value={'encoding': 'Big5', 'confidence': 0.99, 'language': 'Chinese'},
        ):
            detected_encoding = detect_encoding(content)
        self.assertNotEqual(codecs.lookup(detected_encoding).name, codecs.lookup('big5').name)
        # It must not raise.
        content.decode(detected_encoding)

    def test_detect_encoding_ignores_unknown_detected_encoding(self) -> None:
        content = _CESIONES_PERIODO_FILE_WITH_NON_ASCII_BYTES
        with mock.patch(
            'cl_sii.libs.charset_utils.chardet.detect',
            return_value={'encoding': 'not-a-real-encoding', 'confidence': 0.99, 'language': ''},
        ):
            detected_encoding = detect_encoding(content)
        # It must not raise.
        content.decode(detected_encoding)
