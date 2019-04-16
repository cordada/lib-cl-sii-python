import difflib
import io
import unittest
from datetime import date

import cl_sii.dte.constants
from cl_sii.libs import xml_utils
from cl_sii.rut import Rut

from cl_sii.dte.parse import (  # noqa: F401
    clean_dte_xml, parse_dte_xml, validate_dte_xml,
    _remove_dte_xml_doc_personalizado, _set_dte_xml_missing_xmlns,
    DTE_XML_SCHEMA_OBJ, DTE_XMLNS, DTE_XMLNS_MAP
)

from .utils import read_test_file_bytes


_TEST_DTE_NEEDS_CLEAN_FILE_PATH = 'test_data/sii-dte/DTE--76354771-K--33--170.xml'


class OthersTest(unittest.TestCase):

    def test_DTE_XML_SCHEMA_OBJ(self) -> None:
        # TODO: implement
        pass

    def test_integration_ok(self) -> None:
        # TODO: split in separate tests, with more coverage.

        dte_bad_xml_file_path = _TEST_DTE_NEEDS_CLEAN_FILE_PATH

        file_bytes = read_test_file_bytes(dte_bad_xml_file_path)
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
        # This would raise:
        # parse_dte_xml(xml_doc)

        xml_doc_cleaned, modified = clean_dte_xml(
            xml_doc,
            set_missing_xmlns=True,
            remove_doc_personalizado=True,
        )
        self.assertTrue(modified)

        # This will not raise.
        validate_dte_xml(xml_doc_cleaned)

        self.assertEqual(
            xml_doc_cleaned.getroottree().getroot().tag,
            '{%s}DTE' % DTE_XMLNS)

        f = io.BytesIO()
        xml_utils.write_xml_doc(xml_doc_cleaned, f)
        file_bytes_rewritten = f.getvalue()
        del f

        xml_doc_rewritten = xml_utils.parse_untrusted_xml(file_bytes_rewritten)
        validate_dte_xml(xml_doc_rewritten)
        parsed_dte_rewritten = parse_dte_xml(xml_doc_cleaned)

        self.assertDictEqual(
            dict(parsed_dte_rewritten.as_dict()),
            dict(
                emisor_rut=Rut('76354771-K'),
                tipo_dte=cl_sii.dte.constants.TipoDteEnum.FACTURA_ELECTRONICA,
                folio=170,
                fecha_emision_date=date(2019, 4, 1),
                receptor_rut=Rut('96790240-3'),
                monto_total=2996301,
                emisor_razon_social='INGENIERIA ENACON SPA',
                receptor_razon_social='MINERA LOS PELAMBRES',
                fecha_vencimiento_date=None,
            ))

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


class FunctionCleanDteXmlTest(unittest.TestCase):

    def test_clean_dte_xml_ok(self) -> None:
        # TODO: implement
        pass

    def test_clean_dte_xml_fail(self) -> None:
        # TODO: implement
        pass

    def test__set_dte_xml_missing_xmlns_ok(self) -> None:
        # TODO: implement
        pass

    def test__set_dte_xml_missing_xmlns_fail(self) -> None:
        # TODO: implement
        pass

    def test__remove_dte_xml_doc_personalizado_ok(self) -> None:
        # TODO: implement
        pass

    def test__remove_dte_xml_doc_personalizado_fail(self) -> None:
        # TODO: implement
        pass


class FunctionParseDteXmlTest(unittest.TestCase):

    # TODO: implement
    pass


class FunctionValidateDteXmlTest(unittest.TestCase):

    # TODO: implement
    pass
