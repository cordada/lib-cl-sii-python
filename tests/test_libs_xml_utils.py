import io
import unittest

import lxml.etree

from cl_sii.libs.crypto_utils import load_pem_x509_cert

from cl_sii.libs.xml_utils import XmlElement
from cl_sii.libs.xml_utils import (  # noqa: F401
    XmlSyntaxError, XmlFeatureForbidden, XmlSchemaDocValidationError,
    XmlSignatureInvalid, XmlSignatureInvalidCertificate, XmlSignatureUnverified,
    parse_untrusted_xml, read_xml_schema, validate_xml_doc, verify_xml_signature, write_xml_doc,
)

from .utils import read_test_file_bytes


class FunctionParseUntrustedXmlTests(unittest.TestCase):

    def test_parse_untrusted_xml_valid(self) -> None:
        value = (
            b'<root>\n'
            b'   <element key="value">text</element>\n'
            b'   <element>text</element>tail\n'
            b'   <empty-element/>\n'
            b'</root>')
        xml = parse_untrusted_xml(value)
        self.assertIsInstance(xml, XmlElement)
        self.assertEqual(
            lxml.etree.tostring(xml, pretty_print=False),
            value)

    def test_bytes_text(self) -> None:
        value = b'not xml'  # type: ignore
        with self.assertRaises(XmlSyntaxError) as cm:
            parse_untrusted_xml(value)

        self.assertSequenceEqual(
            cm.exception.args,
            ("XML syntax error. Start tag expected, '<' not found, line 1, column 1.", )
        )

    def test_attack_billion_laughs_1(self) -> None:
        value = read_test_file_bytes('test_data/xml/attacks/billion-laughs-1.xml')
        with self.assertRaises(XmlSyntaxError) as cm:
            parse_untrusted_xml(value)

        self.assertSequenceEqual(
            cm.exception.args,
            ("XML syntax error. Detected an entity reference loop, line 1, column 7.", )
        )

    def test_attack_billion_laughs_2(self) -> None:
        value = read_test_file_bytes('test_data/xml/attacks/billion-laughs-2.xml')
        with self.assertRaises(XmlSyntaxError) as cm:
            parse_untrusted_xml(value)

        self.assertSequenceEqual(
            cm.exception.args,
            ("XML syntax error. Detected an entity reference loop, line 1, column 4.", )
        )

    def test_attack_quadratic_blowup(self) -> None:
        value = read_test_file_bytes('test_data/xml/attacks/quadratic-blowup-entity-expansion.xml')
        with self.assertRaises(XmlFeatureForbidden) as cm:
            parse_untrusted_xml(value)

        self.assertSequenceEqual(
            cm.exception.args,
            ("XML uses or contains a forbidden feature.", )
        )

    def test_attack_external_entity_expansion_remote(self) -> None:
        value = read_test_file_bytes('test_data/xml/attacks/external-entity-expansion-remote.xml')
        with self.assertRaises(XmlFeatureForbidden) as cm:
            parse_untrusted_xml(value)

        self.assertSequenceEqual(
            cm.exception.args,
            ("XML uses or contains a forbidden feature.", )
        )

    def test_type_error(self) -> None:
        value = 1  # type: ignore
        with self.assertRaises(TypeError) as cm:
            parse_untrusted_xml(value)

        self.assertSequenceEqual(
            cm.exception.args,
            ("Value to be parsed as XML must be bytes.", )
        )


class FunctionReadXmlSchemaTest(unittest.TestCase):

    # TODO: implement

    pass


class FunctionValidateXmlDocTest(unittest.TestCase):

    # TODO: implement

    pass


class FunctionWriteXmlDocTest(unittest.TestCase):

    # TODO: implement for function 'write_xml_doc'. Consider each of the "observations".
    pass


class FunctionVerifyXmlSignatureTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.any_x509_cert_pem_file = read_test_file_bytes(
            'test_data/crypto/wildcard-google-com-cert.pem')

        cls.xml_doc_cert_pem_bytes = read_test_file_bytes(
            'test_data/sii-crypto/DTE--76354771-K--33--170-cert.pem')
        cls.xml_doc_2_cert_pem_bytes = read_test_file_bytes(
            'test_data/sii-crypto/DTE--76399752-9--33--25568-cert.pem')

        cls.with_valid_signature = read_test_file_bytes(
            'test_data/sii-dte/DTE--76354771-K--33--170--cleaned.xml')
        cls.with_valid_signature_signed_data = read_test_file_bytes(
            'test_data/sii-dte/DTE--76354771-K--33--170--cleaned-signed_data.xml')
        cls.with_valid_signature_signed_xml = read_test_file_bytes(
            'test_data/sii-dte/DTE--76354771-K--33--170--cleaned-signed_xml.xml')
        cls.with_valid_signature_signature_xml = read_test_file_bytes(
            'test_data/sii-dte/DTE--76354771-K--33--170--cleaned-signature_xml.xml')

        cls.trivial_without_signature = read_test_file_bytes(
            'test_data/xml/trivial-doc.xml')
        cls.with_too_many_signatures = read_test_file_bytes(
            'test_data/sii-rtc/AEC--76354771-K--33--170--SEQ-2.xml')
        cls.without_signature = read_test_file_bytes(
            'test_data/sii-dte/DTE--76354771-K--33--170--cleaned-mod-removed-signature.xml')
        cls.with_bad_cert = read_test_file_bytes(
            'test_data/sii-dte/DTE--76354771-K--33--170--cleaned-mod-bad-cert.xml')
        cls.with_bad_cert_no_base64 = read_test_file_bytes(
            'test_data/sii-dte/DTE--76354771-K--33--170--cleaned-mod-bad-cert-no-base64.xml')
        cls.with_signature_and_modified = read_test_file_bytes(
            'test_data/sii-dte/DTE--76354771-K--33--170--cleaned-mod-changed-monto.xml')
        cls.with_replaced_cert = read_test_file_bytes(
            'test_data/sii-dte/DTE--76354771-K--33--170--cleaned-mod-replaced-cert.xml')

    def test_ok_external_trusted_cert(self) -> None:
        xml_doc = parse_untrusted_xml(self.with_valid_signature)
        cert = load_pem_x509_cert(self.xml_doc_cert_pem_bytes)

        signed_data, signed_xml, signature_xml = verify_xml_signature(
            xml_doc, trusted_x509_cert=cert)

        self.assertEqual(signed_data, self.with_valid_signature_signed_data)

        f = io.BytesIO()
        write_xml_doc(signed_xml, f)
        signed_xml_bytes = f.getvalue()
        self.assertEqual(signed_xml_bytes, self.with_valid_signature_signed_xml)

        f = io.BytesIO()
        write_xml_doc(signature_xml, f)
        signature_xml_bytes = f.getvalue()
        self.assertEqual(signature_xml_bytes, self.with_valid_signature_signature_xml)

    def test_ok_cert_in_signature(self) -> None:
        # TODO: implement!

        # xml_doc = parse_untrusted_xml(...)
        # verify_xml_signature(xml_doc, trusted_x509_cert=None)
        pass

    def test_fail_cert_type_error(self) -> None:
        xml_doc = parse_untrusted_xml(self.with_valid_signature)
        cert = self.any_x509_cert_pem_file

        with self.assertRaises(TypeError) as cm:
            _ = verify_xml_signature(xml_doc, trusted_x509_cert=cert)
        self.assertEqual(
            cm.exception.args,
            ("'trusted_x509_cert' must be a 'crypto_utils.X509Cert' instance, or None.", ))

    def test_fail_xml_doc_type_error(self) -> None:
        cert = self.any_x509_cert_pem_file

        with self.assertRaises(TypeError) as cm:
            _ = verify_xml_signature(xml_doc=object(), trusted_x509_cert=cert)
        self.assertEqual(
            cm.exception.args,
            ("'xml_doc' must be an XML document/element.", ))

    def test_fail_verify_with_other_cert(self) -> None:
        xml_doc = parse_untrusted_xml(self.with_valid_signature_signature_xml)
        cert = load_pem_x509_cert(self.xml_doc_2_cert_pem_bytes)

        with self.assertRaises(XmlSignatureInvalid) as cm:
            verify_xml_signature(xml_doc, trusted_x509_cert=cert)
        self.assertEqual(
            cm.exception.args,
            ("Signature verification failed: wrong signature length", ))

    def test_bad_cert_included(self) -> None:
        # If the included certificate is bad, it does not matter, as long as it does not break XML.
        xml_doc_with_bad_cert = parse_untrusted_xml(self.with_bad_cert)
        xml_doc_with_bad_cert_no_base64 = parse_untrusted_xml(self.with_bad_cert_no_base64)

        cert = load_pem_x509_cert(self.xml_doc_cert_pem_bytes)

        verify_xml_signature(xml_doc_with_bad_cert, trusted_x509_cert=cert)

        with self.assertRaises(XmlSchemaDocValidationError) as cm:
            verify_xml_signature(xml_doc_with_bad_cert_no_base64, trusted_x509_cert=cert)
        self.assertEqual(
            cm.exception.args,
            ("Element '{http://www.w3.org/2000/09/xmldsig#}X509Certificate': '\nabc\n"
             "' is not a valid value of the atomic type 'xs:base64Binary'., line 30", ))

    def test_fail_replaced_cert(self) -> None:
        xml_doc = parse_untrusted_xml(self.with_replaced_cert)
        cert = load_pem_x509_cert(self.any_x509_cert_pem_file)

        with self.assertRaises(XmlSignatureInvalid) as cm:
            verify_xml_signature(xml_doc, trusted_x509_cert=cert)
        self.assertEqual(
            cm.exception.args,
            ("Signature verification failed: header too long", ))

    def test_fail_included_cert_not_from_a_known_ca(self) -> None:
        xml_doc = parse_untrusted_xml(self.with_valid_signature)

        # Without cert: fails because the issuer of the cert in the signature is not a known CA.
        with self.assertRaises(XmlSignatureInvalidCertificate) as cm:
            verify_xml_signature(xml_doc, trusted_x509_cert=None)
        self.assertEqual(
            cm.exception.args,
            ("[20, 0, 'unable to get local issuer certificate']", ))

    def test_fail_signed_data_modified(self) -> None:
        xml_doc = parse_untrusted_xml(self.with_signature_and_modified)
        cert = load_pem_x509_cert(self.xml_doc_cert_pem_bytes)

        with self.assertRaises(XmlSignatureUnverified) as cm:
            verify_xml_signature(xml_doc, trusted_x509_cert=cert)
        self.assertEqual(cm.exception.args, ("Digest mismatch for reference 0", ))

    def test_xml_doc_without_signature_1(self) -> None:
        xml_doc = parse_untrusted_xml(self.without_signature)

        expected_exc_args = (
            'Invalid input.',
            'Expected to find XML element Signature in {http://www.sii.cl/SiiDte}DTE')

        # Without cert:
        with self.assertRaises(ValueError) as cm:
            verify_xml_signature(xml_doc, trusted_x509_cert=None)
        self.assertEqual(cm.exception.args, expected_exc_args)

        # With cert:
        cert = load_pem_x509_cert(self.any_x509_cert_pem_file)
        with self.assertRaises(ValueError) as cm:
            verify_xml_signature(xml_doc, trusted_x509_cert=cert)
        self.assertEqual(cm.exception.args, expected_exc_args)

    def test_fail_xml_doc_without_signature_2(self) -> None:
        xml_doc = parse_untrusted_xml(self.trivial_without_signature)

        expected_exc_args = (
            'Invalid input.', 'Expected to find XML element Signature in data')

        # Without cert:
        with self.assertRaises(ValueError) as cm:
            verify_xml_signature(xml_doc, trusted_x509_cert=None)
        self.assertEqual(cm.exception.args, expected_exc_args)

        # With cert:
        cert = load_pem_x509_cert(self.xml_doc_cert_pem_bytes)
        with self.assertRaises(ValueError) as cm:
            verify_xml_signature(xml_doc, trusted_x509_cert=cert)
        self.assertEqual(cm.exception.args, expected_exc_args)

    def test_fail_xml_doc_with_too_many_signatures(self) -> None:
        xml_doc = parse_untrusted_xml(self.with_too_many_signatures)

        expected_exc_args = ("XML document with more than one signature is not supported.", )

        # Without cert:
        with self.assertRaises(NotImplementedError) as cm:
            verify_xml_signature(xml_doc, trusted_x509_cert=None)
        self.assertEqual(cm.exception.args, expected_exc_args)

        # With cert:
        cert = load_pem_x509_cert(self.xml_doc_cert_pem_bytes)
        with self.assertRaises(NotImplementedError) as cm:
            verify_xml_signature(xml_doc, trusted_x509_cert=cert)
        self.assertEqual(cm.exception.args, expected_exc_args)

    def test_fail_custom_xml_verifier_invalid_class(self) -> None:
        xml_doc = parse_untrusted_xml(self.trivial_without_signature)
        custom_xml_verifier = object()

        expected_exc_args = (
            "'xml_verifier' must be an instance of 'signxml.XMLVerifier' or of a subclass of it.",
        )

        with self.assertRaises(TypeError) as assert_raises_cm:
            verify_xml_signature(
                xml_doc,
                xml_verifier=custom_xml_verifier,
            )

        self.assertEqual(assert_raises_cm.exception.args, expected_exc_args)
