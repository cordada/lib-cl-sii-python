import codecs
import tempfile
import unittest

from cl_sii.libs.charset_utils import clean_unicode, detect_encoding, detect_file_encoding


# Contents of a fictional file of "cesiones" of a period, modeled after a real one retrieved from
# the SII that used to make 'detect_file_encoding' return 'big5' and thus make the parsing fail
# with a 'UnicodeDecodeError'. All RUTs, company names and emails below are made up.
# The non-ASCII byte is in "N\xfdCLEO DE PRUEBA SPA".
_CESIONES_PERIODO_FILE_WITH_NON_ASCII_BYTES = (
    b'DATOS_CONSULTA; RUT=11111111-1;TIPO_CONSULTA=DEUDOR;DESDE_DDMMAAAA=24032025;'
    b'HASTA_DDMMAAAA=30032025\r\n'
    b'VENDEDOR;ESTADO_CESION;DEUDOR;MAIL_DEUDOR;TIPO_DOC;NOMBRE_DOC;FOLIO_DOC;'
    b'FCH_EMIS_DTE;MNT_TOTAL;CEDENTE;RZ_CEDENTE;MAIL_CEDENTE;CESIONARIO;'
    b'RZ_CESIONARIO;MAIL_CESIONARIO;FCH_CESION;MNT_CESION;FCH_VENCIMIENTO\r\n'
    b'22222222-2;Cesion Vigente;11111111-1;null;33;Factura Electronica;1001;'
    b'2025-03-24;100000;22222222-2;N\xfdCLEO DE PRUEBA SPA;contacto@ejemplo-uno.cl;'
    b'33333333-3;Factoring de Prueba S.A;contacto@ejemplo-dos.cl;'
    b'2025-03-24 19:23;100000;2025-05-23\r\n'
    b'22222222-2;Cesion Vigente;11111111-1;null;33;Factura Electronica;1002;'
    b'2025-03-27;200000;22222222-2;N\xfdCLEO DE PRUEBA SPA;contacto@ejemplo-tres.cl;'
    b'44444444-4;Otra Factoring de Prueba S.A.;contacto@ejemplo-cuatro.cl;'
    b'2025-03-27 17:23;200000;2025-05-26\r\n'
)


class FunctionsTest(unittest.TestCase):
    def test_clean_unicode(self) -> None:
        # %% -----Arrange-----

        expected = 'É'

        # %% -----Act-----

        results = [
            clean_unicode('É'),
            clean_unicode('É'),
            clean_unicode('É'),
            clean_unicode('\N{LATIN CAPITAL LETTER E WITH ACUTE}'),
            clean_unicode('\N{LATIN CAPITAL LETTER E}\N{COMBINING ACUTE ACCENT}'),
        ]

        # %% -----Assert-----

        for result in results:
            self.assertEqual(expected, result)

        # %% -----

    def test_clean_unicode_empty_string(self) -> None:
        # %% -----Arrange-----

        empty_string = ''

        # %% -----Act-----

        result = clean_unicode(empty_string)

        # %% -----Assert-----

        self.assertEqual(empty_string, result)

        # %% -----

    def test_detect_encoding_utf8(self) -> None:
        # %% -----Arrange-----

        content = 'Este es un texto en español con acentos y ñ'.encode('utf-8')
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name

        # %% -----Act-----

        result = detect_file_encoding(temp_file_path)

        # %% -----Assert-----

        self.assertEqual('utf-8', result)

        # %% -----

    def test_detect_encoding_ascii(self) -> None:
        # %% -----Arrange-----

        content = 'This is a simple ASCII text.'.encode('ascii')
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name

        # %% -----Act-----

        result = detect_file_encoding(temp_file_path)

        # %% -----Assert-----

        self.assertEqual('utf-8', result)

        # %% -----

    def test_detect_encoding_default(self) -> None:
        """
        The file does not match any known encoding, so an encoding that decodes any byte sequence
        should be returned.
        """
        # %% -----Arrange-----

        content = b'\x80\x81\x82\x83\x84\x85'
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name

        # %% -----Act-----

        result = detect_file_encoding(temp_file_path)

        # %% -----Assert-----

        self.assertEqual('latin-1', result)

        # %% -----

    def test_detect_encoding_of_empty_data(self) -> None:
        # %% -----Arrange-----

        content = b''

        # %% -----Act-----

        result = detect_encoding(content)

        # %% -----Assert-----

        self.assertEqual('utf-8', result)

        # %% -----

    def test_detect_encoding_of_ascii_data(self) -> None:
        # %% -----Arrange-----

        content = b'This is a simple ASCII text.'

        # %% -----Act-----

        result = detect_encoding(content)

        # %% -----Assert-----

        self.assertEqual('utf-8', result)

        # %% -----

    def test_detect_encoding_of_utf8_data(self) -> None:
        # %% -----Arrange-----

        content = 'Este es un texto en español con acentos y ñ'.encode('utf-8')

        # %% -----Act-----

        result = detect_encoding(content)

        # %% -----Assert-----

        self.assertEqual('utf-8', result)

        # %% -----

    def test_detect_encoding_of_utf8_sample_truncated_mid_character(self) -> None:
        """
        A sample of a larger file may be cut in the middle of a multi-byte character.
        """
        # %% -----Arrange-----

        content = ('Este es un texto en español con acentos y ñ' * 100).encode('utf-8')
        self.assertTrue(content.endswith(b'\xc3\xb1'))
        truncated_content = content[:-1]

        # %% -----Act-----

        result = detect_encoding(truncated_content, is_sample=True)

        # %% -----Assert-----

        self.assertEqual('utf-8', result)

        # %% -----

    def test_detect_encoding_of_complete_data_truncated_mid_character(self) -> None:
        """
        If the data is not a sample, the returned encoding must be able to decode all of it.
        """
        # %% -----Arrange-----

        contents = (
            b'\xc3',
            ('Este es un texto en español con acentos y ñ' * 100).encode('utf-8')[:-1],
        )

        for content in contents:
            with self.subTest(content=content[:20]):
                # %% -----Act-----

                detected_encoding = detect_encoding(content)

                # %% -----Assert-----

                # It must not raise.
                content.decode(detected_encoding)

        # %% -----

    def test_detect_encoding_of_legacy_8_bit_data(self) -> None:
        # %% -----Arrange-----

        text = 'Cesión Vigente;MI CAÑOPITO SA;Factura Electrónica' * 20

        for encoding in ('iso-8859-1', 'cp1252'):
            with self.subTest(encoding=encoding):
                content = text.encode(encoding)

                # %% -----Act-----

                result = detect_encoding(content)

                # %% -----Assert-----

                # note: an "iso-8859-1" input is decoded as "cp1252", which for this text is
                #   equivalent: both share the whole 0xA0-0xFF range.
                self.assertEqual('cp1252', result)
                self.assertEqual(text, content.decode(result))

        # %% -----

    def test_detect_encoding_of_data_with_bom(self) -> None:
        # %% -----Arrange-----

        text = 'Cesión Vigente'
        cases = (
            (b'', 'utf-8-sig', 'utf-8-sig'),
            (b'', 'utf-16', 'utf-16'),
            (codecs.BOM_UTF16_LE, 'utf-16-le', 'utf-16'),
            (codecs.BOM_UTF16_BE, 'utf-16-be', 'utf-16'),
            (b'', 'utf-32', 'utf-32'),
        )

        for bom, encoding, expected_encoding in cases:
            with self.subTest(encoding=encoding):
                content = bom + text.encode(encoding)

                # %% -----Act-----

                result = detect_encoding(content)

                # %% -----Assert-----

                self.assertEqual(expected_encoding, result)
                self.assertEqual(text, content.decode(expected_encoding))

        # %% -----

    def test_detect_encoding_of_data_with_a_few_non_ascii_bytes(self) -> None:
        """
        Regression test: this data used to be detected as 'big5', which can not decode it.
        """
        # %% -----Arrange-----

        content = _CESIONES_PERIODO_FILE_WITH_NON_ASCII_BYTES

        # %% -----Act-----

        result = detect_encoding(content)

        # %% -----Assert-----

        self.assertEqual('cp1252', result)
        # It must not raise.
        content.decode(result)

        # %% -----

    def test_detect_encoding_of_utf16_data_without_bom(self) -> None:
        """
        UTF-16 is recognized only by its byte order mark. Without one, the data is decoded by the
        first candidate encoding that accepts it, and the caller finds out further down.
        """
        # %% -----Arrange-----

        content = ('Cesión Vigente;Factura Electrónica\r\n' * 20).encode('utf-16-le')

        # %% -----Act-----

        result = detect_encoding(content)

        # %% -----Assert-----

        self.assertNotEqual('utf-16', result)

        # %% -----
