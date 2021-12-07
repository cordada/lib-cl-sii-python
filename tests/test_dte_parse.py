import difflib
import io
import unittest
from datetime import date, datetime

import cl_sii.dte.constants
from cl_sii.dte.data_models import DteDataL2
from cl_sii.libs import crypto_utils
from cl_sii.libs import encoding_utils
from cl_sii.libs import tz_utils
from cl_sii.libs import xml_utils
from cl_sii.rut import Rut

from cl_sii.dte.parse import (  # noqa: F401
    clean_dte_xml, parse_dte_xml, validate_dte_xml,
    _remove_dte_xml_doc_personalizado, _set_dte_xml_missing_xmlns,
    DTE_XML_SCHEMA_OBJ, DTE_XMLNS, DTE_XMLNS_MAP
)

from .utils import read_test_file_bytes


class OthersTest(unittest.TestCase):

    def test_DTE_XML_SCHEMA_OBJ(self) -> None:
        # TODO: implement
        pass


class FunctionValidateDteXmlTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.dte_bad_xml_1_xml_bytes = read_test_file_bytes(
            'test_data/sii-dte/DTE--76354771-K--33--170.xml')
        cls.dte_bad_xml_2_xml_bytes = read_test_file_bytes(
            'test_data/sii-dte/DTE--76399752-9--33--25568.xml')
        cls.dte_bad_xml_3_xml_bytes = read_test_file_bytes(
            'test_data/sii-dte/DTE--60910000-1--33--2336600.xml')

        cls.dte_clean_xml_1_xml_bytes = read_test_file_bytes(
            'test_data/sii-dte/DTE--76354771-K--33--170--cleaned.xml')
        cls.dte_clean_xml_2_xml_bytes = read_test_file_bytes(
            'test_data/sii-dte/DTE--76399752-9--33--25568--cleaned.xml')
        cls.dte_clean_xml_3_xml_bytes = read_test_file_bytes(
            'test_data/sii-dte/DTE--60910000-1--33--2336600--cleaned.xml')

    def test_validate_dte_xml_ok_dte_1(self) -> None:
        xml_doc = xml_utils.parse_untrusted_xml(self.dte_clean_xml_1_xml_bytes)
        validate_dte_xml(xml_doc)

        self.assertEqual(
            xml_doc.getroottree().getroot().tag,
            '{%s}DTE' % DTE_XMLNS)

    def test_validate_dte_xml_ok_dte_2(self) -> None:
        xml_doc = xml_utils.parse_untrusted_xml(self.dte_clean_xml_2_xml_bytes)
        validate_dte_xml(xml_doc)

        self.assertEqual(
            xml_doc.getroottree().getroot().tag,
            '{%s}DTE' % DTE_XMLNS)

    def test_validate_dte_xml_ok_dte_3(self) -> None:
        xml_doc = xml_utils.parse_untrusted_xml(self.dte_clean_xml_3_xml_bytes)
        validate_dte_xml(xml_doc)

        self.assertEqual(
            xml_doc.getroottree().getroot().tag,
            '{%s}DTE' % DTE_XMLNS)

    def test_validate_dte_xml_fail_x(self) -> None:
        # TODO: implement more cases
        pass

    def test_validate_dte_xml_fail_dte_1(self) -> None:
        file_bytes = self.dte_bad_xml_1_xml_bytes
        xml_doc = xml_utils.parse_untrusted_xml(file_bytes)

        self.assertEqual(
            xml_doc.getroottree().getroot().tag,
            'DTE')

        with self.assertRaises(xml_utils.XmlSchemaDocValidationError) as cm:
            validate_dte_xml(xml_doc)
        self.assertSequenceEqual(
            cm.exception.args,
            ("Element 'DTE': No matching global declaration available for the validation root., "
             "line 2", )
        )

    def test_validate_dte_xml_fail_dte_2(self) -> None:
        file_bytes = self.dte_bad_xml_2_xml_bytes
        xml_doc = xml_utils.parse_untrusted_xml(file_bytes)

        self.assertEqual(
            xml_doc.getroottree().getroot().tag,
            'DTE')

        with self.assertRaises(xml_utils.XmlSchemaDocValidationError) as cm:
            validate_dte_xml(xml_doc)
        self.assertSequenceEqual(
            cm.exception.args,
            ("Element 'DTE': No matching global declaration available for the validation root., "
             "line 2", )
        )

    def test_validate_dte_xml_fail_dte_3(self) -> None:
        file_bytes = self.dte_bad_xml_3_xml_bytes
        xml_doc = xml_utils.parse_untrusted_xml(file_bytes)

        self.assertEqual(
            xml_doc.getroottree().getroot().tag,
            'DTE')

        with self.assertRaises(xml_utils.XmlSchemaDocValidationError) as cm:
            validate_dte_xml(xml_doc)
        self.assertSequenceEqual(
            cm.exception.args,
            ("Element 'DTE': No matching global declaration available for the validation root., "
             "line 2", )
        )


class FunctionCleanDteXmlTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.dte_bad_xml_1_xml_bytes = read_test_file_bytes(
            'test_data/sii-dte/DTE--76354771-K--33--170.xml')
        cls.dte_bad_xml_2_xml_bytes = read_test_file_bytes(
            'test_data/sii-dte/DTE--76399752-9--33--25568.xml')
        cls.dte_bad_xml_3_xml_bytes = read_test_file_bytes(
            'test_data/sii-dte/DTE--60910000-1--33--2336600.xml')

    def test_clean_dte_xml_ok_1(self) -> None:
        file_bytes = self.dte_bad_xml_1_xml_bytes
        xml_doc = xml_utils.parse_untrusted_xml(file_bytes)

        self.assertEqual(
            xml_doc.getroottree().getroot().tag,
            'DTE')

        with self.assertRaises(xml_utils.XmlSchemaDocValidationError) as cm:
            validate_dte_xml(xml_doc)
        self.assertSequenceEqual(
            cm.exception.args,
            ("Element 'DTE': No matching global declaration available for the validation root., "
             "line 2", )
        )

        xml_doc_cleaned, modified = clean_dte_xml(
            xml_doc,
            set_missing_xmlns=True,
            remove_doc_personalizado=True,
        )
        self.assertTrue(modified)

        # This will not raise.
        validate_dte_xml(xml_doc_cleaned)

        f = io.BytesIO()
        xml_utils.write_xml_doc(xml_doc_cleaned, f)
        file_bytes_rewritten = f.getvalue()
        del f

        xml_doc_rewritten = xml_utils.parse_untrusted_xml(file_bytes_rewritten)
        validate_dte_xml(xml_doc_rewritten)

        expected_file_bytes_diff = (
            b'--- \n',
            b'+++ \n',
            b'@@ -1,5 +1,5 @@\n',
            b'-<?xml version="1.0" encoding="ISO-8859-1"?>',
            b'-<DTE version="1.0">',
            b"+<?xml version='1.0' encoding='ISO-8859-1'?>",
            b'+<DTE xmlns="http://www.sii.cl/SiiDte" version="1.0">',
            b'   <!-- O Win32 Chrome 73 central VERSION: v20190227 -->',
            b' <Documento ID="MiPE76354771-13419">',
            b'     <Encabezado>',
            b'@@ -59,13 +59,13 @@\n',
            b'   </Documento>',
            b' <Signature xmlns="http://www.w3.org/2000/09/xmldsig#">',
            b' <SignedInfo>',
            b'-<CanonicalizationMethod Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315" />',  # noqa: E501
            b'-<SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1" />',
            b'+<CanonicalizationMethod Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"/>',  # noqa: E501
            b'+<SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1"/>',
            b' <Reference URI="#MiPE76354771-13419">',
            b' <Transforms>',
            b'-<Transform Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315" />',
            b'+<Transform Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"/>',
            b' </Transforms>',
            b'-<DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1" />',
            b'+<DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"/>',
            b' <DigestValue>ij2Qn6xOc2eRx3hwyO/GrzptoBk=</DigestValue>',
            b' </Reference>',
            b' </SignedInfo>',
        )

        file_bytes_diff_gen = difflib.diff_bytes(
            dfunc=difflib.unified_diff,
            a=file_bytes.splitlines(),
            b=file_bytes_rewritten.splitlines())
        self.assertSequenceEqual(
            [diff_line for diff_line in file_bytes_diff_gen],
            expected_file_bytes_diff
        )

    def test_clean_dte_xml_ok_2(self) -> None:
        file_bytes = self.dte_bad_xml_2_xml_bytes
        xml_doc = xml_utils.parse_untrusted_xml(file_bytes)

        self.assertEqual(
            xml_doc.getroottree().getroot().tag,
            'DTE')

        with self.assertRaises(xml_utils.XmlSchemaDocValidationError) as cm:
            validate_dte_xml(xml_doc)
        self.assertSequenceEqual(
            cm.exception.args,
            ("Element 'DTE': No matching global declaration available for the validation root., "
             "line 2", )
        )

        xml_doc_cleaned, modified = clean_dte_xml(
            xml_doc,
            set_missing_xmlns=True,
            remove_doc_personalizado=True,
        )
        self.assertTrue(modified)

        # This will not raise.
        validate_dte_xml(xml_doc_cleaned)

        f = io.BytesIO()
        xml_utils.write_xml_doc(xml_doc_cleaned, f)
        file_bytes_rewritten = f.getvalue()
        del f

        xml_doc_rewritten = xml_utils.parse_untrusted_xml(file_bytes_rewritten)
        validate_dte_xml(xml_doc_rewritten)

        expected_file_bytes_diff = (
            b'--- \n',
            b'+++ \n',
            b'@@ -1,5 +1,5 @@\n',
            b'-<?xml version="1.0" encoding="ISO-8859-1"?>',
            b'-<DTE version="1.0">',
            b"+<?xml version='1.0' encoding='ISO-8859-1'?>",
            b'+<DTE xmlns="http://www.sii.cl/SiiDte" version="1.0">',
            b'   <!-- O Win32 Chrome 73 central VERSION: v20190227 -->',
            b' <Documento ID="MiPE76399752-6048">',
            b'     <Encabezado>',
            b'@@ -64,13 +64,13 @@\n',
            b'   </Documento>',
            b' <Signature xmlns="http://www.w3.org/2000/09/xmldsig#">',
            b' <SignedInfo>',
            b'-<CanonicalizationMethod Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315" />',  # noqa: E501
            b'-<SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1" />',
            b'+<CanonicalizationMethod Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"/>',  # noqa: E501
            b'+<SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1"/>',
            b' <Reference URI="#MiPE76399752-6048">',
            b' <Transforms>',
            b'-<Transform Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315" />',
            b'+<Transform Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"/>',
            b' </Transforms>',
            b'-<DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1" />',
            b'+<DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"/>',
            b' <DigestValue>tk/D3mfO/KtdWyFXYZHe7dtYijg=</DigestValue>',
            b' </Reference>',
            b' </SignedInfo>',
        )

        file_bytes_diff_gen = difflib.diff_bytes(
            dfunc=difflib.unified_diff,
            a=file_bytes.splitlines(),
            b=file_bytes_rewritten.splitlines())
        self.assertSequenceEqual(
            [diff_line for diff_line in file_bytes_diff_gen],
            expected_file_bytes_diff
        )

    def test_clean_dte_xml_ok_3(self) -> None:
        file_bytes = self.dte_bad_xml_3_xml_bytes
        xml_doc = xml_utils.parse_untrusted_xml(file_bytes)

        self.assertEqual(
            xml_doc.getroottree().getroot().tag,
            'DTE')

        with self.assertRaises(xml_utils.XmlSchemaDocValidationError) as cm:
            validate_dte_xml(xml_doc)
        self.assertSequenceEqual(
            cm.exception.args,
            ("Element 'DTE': No matching global declaration available for the validation root., "
             "line 2", )
        )

        xml_doc_cleaned, modified = clean_dte_xml(
            xml_doc,
            set_missing_xmlns=True,
            remove_doc_personalizado=True,
        )
        self.assertTrue(modified)

        # This will not raise.
        validate_dte_xml(xml_doc_cleaned)

        f = io.BytesIO()
        xml_utils.write_xml_doc(xml_doc_cleaned, f)
        file_bytes_rewritten = f.getvalue()
        del f

        xml_doc_rewritten = xml_utils.parse_untrusted_xml(file_bytes_rewritten)
        validate_dte_xml(xml_doc_rewritten)

        expected_file_bytes_diff = (
            b'--- \n',
            b'+++ \n',
            b'@@ -1,5 +1,5 @@\n',
            b'-<?xml version="1.0" encoding="windows-1252"?>',
            b'-<DTE version="1.0">',
            b"+<?xml version='1.0' encoding='WINDOWS-1252'?>",
            b'+<DTE xmlns="http://www.sii.cl/SiiDte" version="1.0">',
            b' <Documento ID="DTE-33-2336600">',
            b' <Encabezado>',
            b' <IdDoc>',
        )

        file_bytes_diff_gen = difflib.diff_bytes(
            dfunc=difflib.unified_diff,
            a=file_bytes.splitlines(),
            b=file_bytes_rewritten.splitlines())
        self.assertSequenceEqual(
            [diff_line for diff_line in file_bytes_diff_gen],
            expected_file_bytes_diff
        )

    def test_clean_dte_xml_fail(self) -> None:
        # TODO: implement for 'clean_dte_xml', for many cases.
        pass

    def test__set_dte_xml_missing_xmlns_ok(self) -> None:
        # TODO: implement for '_set_dte_xml_missing_xmlns'.
        pass

    def test__set_dte_xml_missing_xmlns_fail(self) -> None:
        # TODO: implement for '_set_dte_xml_missing_xmlns'.
        pass

    def test__remove_dte_xml_doc_personalizado_ok(self) -> None:
        # TODO: implement for '_remove_dte_xml_doc_personalizado'.
        pass

    def test__remove_dte_xml_doc_personalizado_fail(self) -> None:
        # TODO: implement for '_remove_dte_xml_doc_personalizado'.
        pass


class FunctionParseDteXmlTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.dte_bad_xml_1_xml_bytes = read_test_file_bytes(
            'test_data/sii-dte/DTE--76354771-K--33--170.xml')
        cls.dte_bad_xml_2_xml_bytes = read_test_file_bytes(
            'test_data/sii-dte/DTE--76399752-9--33--25568.xml')
        cls.dte_bad_xml_3_xml_bytes = read_test_file_bytes(
            'test_data/sii-dte/DTE--60910000-1--33--2336600.xml')

        cls.dte_clean_xml_1_xml_bytes = read_test_file_bytes(
            'test_data/sii-dte/DTE--76354771-K--33--170--cleaned.xml')
        cls.dte_clean_xml_2_xml_bytes = read_test_file_bytes(
            'test_data/sii-dte/DTE--76399752-9--33--25568--cleaned.xml')
        cls.dte_clean_xml_3_xml_bytes = read_test_file_bytes(
            'test_data/sii-dte/DTE--60910000-1--33--2336600--cleaned.xml')
        cls.dte_clean_xml_1b_xml_bytes = read_test_file_bytes(
            'test_data/sii-dte/DTE--76354771-K--33--170--cleaned-mod-empty-emails.xml')

        cls.dte_clean_xml_1_cert_pem_bytes = encoding_utils.clean_base64(
            crypto_utils.remove_pem_cert_header_footer(
                read_test_file_bytes('test_data/sii-crypto/DTE--76354771-K--33--170-cert.pem')))
        cls.dte_clean_xml_1_cert_der = read_test_file_bytes(
            'test_data/sii-crypto/DTE--76354771-K--33--170-cert.der')
        cls.dte_clean_xml_2_cert_pem_bytes = encoding_utils.clean_base64(
            crypto_utils.remove_pem_cert_header_footer(
                read_test_file_bytes('test_data/sii-crypto/DTE--76399752-9--33--25568-cert.pem')))
        cls.dte_clean_xml_2_cert_der = read_test_file_bytes(
            'test_data/sii-crypto/DTE--76399752-9--33--25568-cert.der')
        cls.dte_clean_xml_3_cert_pem_bytes = encoding_utils.clean_base64(
            crypto_utils.remove_pem_cert_header_footer(
                read_test_file_bytes('test_data/sii-crypto/DTE--60910000-1--33--2336600-cert.pem')))
        cls.dte_clean_xml_3_cert_der = read_test_file_bytes(
            'test_data/sii-crypto/DTE--60910000-1--33--2336600-cert.der')

        cls._TEST_DTE_1_SIGNATURE_VALUE = encoding_utils.decode_base64_strict(
            read_test_file_bytes(
                'test_data/sii-crypto/DTE--76354771-K--33--170-signature-value-base64.txt'))
        cls._TEST_DTE_2_SIGNATURE_VALUE = encoding_utils.decode_base64_strict(
            read_test_file_bytes(
                'test_data/sii-crypto/DTE--76399752-9--33--25568-signature-value-base64.txt'))
        cls._TEST_DTE_3_SIGNATURE_VALUE = encoding_utils.decode_base64_strict(
            read_test_file_bytes(
                'test_data/sii-crypto/DTE--60910000-1--33--2336600-signature-value-base64.txt'))

    def test_data(self):
        self.assertEqual(
            self._TEST_DTE_1_SIGNATURE_VALUE,
            b'~\xc6\x0f\xe6\x9f\xe55\xfa\x1f\x03?\x0f9(k&:\x97t\x14\xcd6\xdb\xef\xe3\xf4\xd6'
            b'\x0b\x16\xef\xc12\x00^\xbe\xc1.\xb9o_p\xbf\x1e\x97\xe8\xe2\xf8\xaak\x14\xae\xd4'
            b'\xe1\x85\x80\xf9\xe4u\xd0\xc8\x17\x08\xfff\xc5]m\xd0~2\x1aJ\x93(Z\xf3tq\x84\x9a'
            b'X\x05PX\xdd\xcf\xb2\xf4\x9e\xa81\xf7Ht\xc0\x18^\x11$\x17\x0f0\xebr\x87\xca\x17_'
            b'\xd8O]\x9d\xb2\xa2\xc2\xa4\xb1\r\xc6#M>\xaf^\xc2\xcf\xad\x99')
        self.assertEqual(
            self._TEST_DTE_2_SIGNATURE_VALUE,
            b"\xc3\x03\x8cB\xe1jk\xa79\x836\x12'\x93\xd6~\x8d\x0e\x88\x07\xfe\xc8\xd7\t+\xac1"
            b"\xe3\x12wT\xd7\xa1\x94\x07\x0c\xad@v\xab\xea\xca\xfc0\xe1\n\xf8\xf1\x02\x85\xf87"
            b"\x10@\n!C2\xb4\xcc!\xfb\xf1\xaf\x05\xe3-\xddh_~\xe5HS\xad\xb1e\xfa'\x12\xf4I_"
            b"\xad,^\xea\xbd`\xae\xd5\x8c\xf0\xf3*T\x7f\xb1\x83\x91\xbc\xa6&J\x13`1}$Q|\x91"
            b"\x858\x15\xd56\xc2\xdbb\xc2w\xbd\\\x7f\x10\x14x\x17\xb2\x87\n?\xf6\xb2\x83\x08"
            b"\x8exj\xa25\x7fh\xfc\xeeWKa\x96\xa6\xdf\x8a3m#\xae\xfbX\x9f\xb5\x050@\xff\xdd"
            b"\xa3\xdap&\xf5\x18\x00b\xce\xbf&\x95Q\x19\x82\x06`&\xe9\xcc\x0c(i\x15\x0c\x84"
            b"\x8a\x04\x970\xaeH\xef~\xc0s\xc0\xf6o\x0e\xd6\x07\x8e\xd6\x8fU\x81/{\x02\x15\x10"
            b"\xe5]E\xed\x9c\xcb\xc2\x84\x15i\xd0tT]\x8b\x8a\x1f'\xe9\x0b:\x88\x05|\xa0b\xb2"
            b"\x19{\x1cW\x80\xe4\xa7*\xef\xf2\x1a")
        self.assertEqual(
            self._TEST_DTE_3_SIGNATURE_VALUE,
            b"&{\x924\xcd\x80\xe9\xc2\x89pN9\x1ec\xf9\x8b&,\xec\xc8\x08\xa6[\x8ajo\xad\xed"
            b"\x84_US+\xb57\x89\x997\xc5~\xd7#\xf25C\xa8\xa1\x06\xb4\xd0*\x15\x0b\xe3i[\x9b"
            b"\x9b\x1a\x9c\xfclb\x10\x86o\xdb\xb5\x91|\x1c\x03\xefV\xcb\xf4]\x82\x82<p\xeb"
            b"\xeb\xad\x0e\x069\xd5\xb7\xba\xbcy\x0c<\xfd\xcc\tE\xff\xb8\x1f\x99\xd5\x99\xfd"
            b"\x8c\xce\x14\xfd\x11\xb3\x9cO5\xed\xa68kc\xd4\x16\xa7zoU.\x13A\xca\xa3\xf4p@\x07"
            b"\x06\xb3\x16W\x1a\x89Y\xdeu\x05\xe3\x8d\xd0\x88\xbe\xab\x89\x1f\x9e\xf0\xc6\x92H"
            b"\x92\xc9lg2\x90\x99G\x87\x8e\x0c4&\x11b\x86\x1b\xc2\xe0)\xea` \xe6\x1f6\xcf\xc1"
            b"\x1a\xce/\x05\xf8-\x12f\xf4\n!0\xa0wWh\xf8f`4e\t\x07T\x1a+\xf29\xacN\xd6\r\xf8k"
            b"\xe6\x83\xb0\xaaMEy\x03\x08/\xf4\x19\xa8s\x91x\x8c\xa8\x1e\xbe\xd6Ur)5\x06\x8e"
            b"\xfcr\xa5W\x8e\x9dJ\xe5\xb3d")

        self.assertEqual(
            crypto_utils.x509_cert_pem_to_der(self.dte_clean_xml_1_cert_pem_bytes),
            self.dte_clean_xml_1_cert_der)
        self.assertEqual(
            crypto_utils.x509_cert_pem_to_der(self.dte_clean_xml_2_cert_pem_bytes),
            self.dte_clean_xml_2_cert_der)
        self.assertEqual(
            crypto_utils.x509_cert_pem_to_der(self.dte_clean_xml_3_cert_pem_bytes),
            self.dte_clean_xml_3_cert_der)

    def test_parse_dte_xml_ok_1(self) -> None:
        xml_doc = xml_utils.parse_untrusted_xml(self.dte_clean_xml_1_xml_bytes)

        dte_xml_data = parse_dte_xml(xml_doc)
        self.assertDictEqual(
            dict(dte_xml_data.as_dict()),
            dict(
                emisor_rut=Rut('76354771-K'),
                tipo_dte=cl_sii.dte.constants.TipoDte.FACTURA_ELECTRONICA,
                folio=170,
                fecha_emision_date=date(2019, 4, 1),
                receptor_rut=Rut('96790240-3'),
                monto_total=2996301,
                emisor_razon_social='INGENIERIA ENACON SPA',
                receptor_razon_social='MINERA LOS PELAMBRES',
                fecha_vencimiento_date=None,
                firma_documento_dt=tz_utils.convert_naive_dt_to_tz_aware(
                    dt=datetime(2019, 4, 1, 1, 36, 40),
                    tz=DteDataL2.DATETIME_FIELDS_TZ),
                signature_value=self._TEST_DTE_1_SIGNATURE_VALUE,
                signature_x509_cert_der=self.dte_clean_xml_1_cert_der,
                emisor_giro='Ingenieria y Construccion',
                emisor_email='ENACONLTDA@GMAIL.COM',
                receptor_email=None,
            ))

    def test_parse_dte_xml_ok_3(self) -> None:
        xml_doc = xml_utils.parse_untrusted_xml(self.dte_clean_xml_3_xml_bytes)

        dte_xml_data = parse_dte_xml(xml_doc)
        self.assertDictEqual(
            dict(dte_xml_data.as_dict()),
            dict(
                emisor_rut=Rut('60910000-1'),
                tipo_dte=cl_sii.dte.constants.TipoDte.FACTURA_ELECTRONICA,
                folio=2336600,
                fecha_emision_date=date(2019, 8, 8),
                receptor_rut=Rut('76555835-2'),
                monto_total=10642,
                emisor_razon_social='Universidad de Chile',
                receptor_razon_social='FYNPAL SPA',
                fecha_vencimiento_date=date(2019, 8, 8),
                firma_documento_dt=tz_utils.convert_naive_dt_to_tz_aware(
                    dt=datetime(2019, 8, 9, 9, 41, 9),
                    tz=DteDataL2.DATETIME_FIELDS_TZ),
                signature_value=self._TEST_DTE_3_SIGNATURE_VALUE,
                signature_x509_cert_der=self.dte_clean_xml_3_cert_der,
                emisor_giro='Corporación Educacional y Servicios                 Profesionales',
                emisor_email=None,
                receptor_email=None,
            ))

    def test_parse_dte_xml_ok_1b(self) -> None:
        xml_doc = xml_utils.parse_untrusted_xml(self.dte_clean_xml_1b_xml_bytes)

        dte_xml_data = parse_dte_xml(xml_doc)
        self.assertDictEqual(
            dict(dte_xml_data.as_dict()),
            dict(
                emisor_rut=Rut('76354771-K'),
                tipo_dte=cl_sii.dte.constants.TipoDte.FACTURA_ELECTRONICA,
                folio=170,
                fecha_emision_date=date(2019, 4, 1),
                receptor_rut=Rut('96790240-3'),
                monto_total=2996301,
                emisor_razon_social='INGENIERIA ENACON SPA',
                receptor_razon_social='MINERA LOS PELAMBRES',
                fecha_vencimiento_date=None,
                firma_documento_dt=tz_utils.convert_naive_dt_to_tz_aware(
                    dt=datetime(2019, 4, 1, 1, 36, 40),
                    tz=DteDataL2.DATETIME_FIELDS_TZ),
                signature_value=self._TEST_DTE_1_SIGNATURE_VALUE,
                signature_x509_cert_der=self.dte_clean_xml_1_cert_der,
                emisor_giro='Ingenieria y Construccion',
                emisor_email=None,
                receptor_email=None,
            ))

    def test_parse_dte_xml_ok_2(self) -> None:
        xml_doc = xml_utils.parse_untrusted_xml(self.dte_clean_xml_2_xml_bytes)

        dte_xml_data = parse_dte_xml(xml_doc)
        self.assertDictEqual(
            dict(dte_xml_data.as_dict()),
            dict(
                emisor_rut=Rut('76399752-9'),
                tipo_dte=cl_sii.dte.constants.TipoDte.FACTURA_ELECTRONICA,
                folio=25568,
                fecha_emision_date=date(2019, 3, 29),
                receptor_rut=Rut('96874030-K'),
                monto_total=230992,
                emisor_razon_social='COMERCIALIZADORA INNOVA MOBEL SPA',
                receptor_razon_social='EMPRESAS LA POLAR S.A.',
                fecha_vencimiento_date=None,
                firma_documento_dt=tz_utils.convert_naive_dt_to_tz_aware(
                    dt=datetime(2019, 3, 28, 13, 59, 52),
                    tz=DteDataL2.DATETIME_FIELDS_TZ),
                signature_value=self._TEST_DTE_2_SIGNATURE_VALUE,
                signature_x509_cert_der=self.dte_clean_xml_2_cert_der,
                emisor_giro='COMERCIALIZACION DE PRODUCTOS PARA EL HOGAR',
                emisor_email='ANGEL.PEZO@APCASESORIAS.CL',
                receptor_email=None,
            ))

    def test_parse_dte_xml_fail_x(self) -> None:
        # TODO: implement more cases
        pass

    def test_parse_dte_xml_fail_1(self) -> None:
        xml_doc = xml_utils.parse_untrusted_xml(self.dte_bad_xml_1_xml_bytes)

        with self.assertRaises(ValueError) as cm:
            parse_dte_xml(xml_doc)
        self.assertSequenceEqual(
            cm.exception.args,
            ("Top level XML element 'Document' is required.", )
        )

    def test_parse_dte_xml_fail_2(self) -> None:
        xml_doc = xml_utils.parse_untrusted_xml(self.dte_bad_xml_2_xml_bytes)

        with self.assertRaises(ValueError) as cm:
            parse_dte_xml(xml_doc)
        self.assertSequenceEqual(
            cm.exception.args,
            ("Top level XML element 'Document' is required.", )
        )

    def test_parse_dte_xml_fail_3(self) -> None:
        xml_doc = xml_utils.parse_untrusted_xml(self.dte_bad_xml_3_xml_bytes)

        with self.assertRaises(ValueError) as cm:
            parse_dte_xml(xml_doc)
        self.assertSequenceEqual(
            cm.exception.args,
            ("Top level XML element 'Document' is required.", )
        )
