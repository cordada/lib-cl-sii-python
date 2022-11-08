from __future__ import annotations

import dataclasses
import io
import unittest

from cl_sii.libs.crypto_utils import load_pem_x509_cert
from cl_sii.libs.xml_utils import parse_untrusted_xml, verify_xml_signature, write_xml_doc
from cl_sii.rtc.parse_aec import parse_aec_xml
from cl_sii.rtc.xml_utils import AecXMLVerifier, verify_aec_signature
from .utils import read_test_file_bytes


class AecXmlValidatorTest(unittest.TestCase):
    """
    Tests for :class:`AecXMLVerifier`.
    """

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.xml_doc_cert_pem_bytes = read_test_file_bytes(
            'test_data/sii-crypto/AEC--76354771-K--33--170--SEQ-2-cert.pem',
        )

        cls.with_valid_signature = read_test_file_bytes(
            'test_data/sii-rtc/AEC--76354771-K--33--170--SEQ-2-canonicalized-c14n.xml',
        )
        cls.with_valid_signature_signed_data = read_test_file_bytes(
            'test_data/sii-rtc/AEC--76354771-K--33--170--SEQ-2-canonicalized-c14n-signed_data.xml',
        )
        cls.with_valid_signature_signed_xml = read_test_file_bytes(
            'test_data/sii-rtc/AEC--76354771-K--33--170--SEQ-2-canonicalized-c14n-signed_xml.xml',
        )
        cls.with_valid_signature_signature_xml = read_test_file_bytes(
            'test_data/sii-rtc/AEC--76354771-K--33--170--SEQ-2-canonicalized-c14n-signature_xml.xml',  # noqa: E501
        )

    def test_xml_utils_verify_xml_signature_ok_external_trusted_cert(self) -> None:
        xml_doc = parse_untrusted_xml(self.with_valid_signature)
        cert = load_pem_x509_cert(self.xml_doc_cert_pem_bytes)
        aec_xml_verifier = AecXMLVerifier()

        # Workaround for breaking change in signxml 2.10.0 and 2.10.1:
        # (See https://github.com/XML-Security/signxml/blob/v2.10.1/Changes.rst)
        aec_xml_verifier.excise_empty_xmlns_declarations = True

        signed_data, signed_xml, signature_xml = verify_xml_signature(
            xml_doc,
            trusted_x509_cert=cert,
            xml_verifier=aec_xml_verifier,
            xml_verifier_supports_multiple_signatures=True,
        )

        self.assertEqual(signed_data, self.with_valid_signature_signed_data)

        f = io.BytesIO()
        write_xml_doc(signed_xml, f)
        signed_xml_bytes = f.getvalue()
        self.assertEqual(signed_xml_bytes, self.with_valid_signature_signed_xml)

        f = io.BytesIO()
        write_xml_doc(signature_xml, f)
        signature_xml_bytes = f.getvalue()
        self.assertEqual(signature_xml_bytes, self.with_valid_signature_signature_xml)


class FunctionVerifyAecSignatureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.xml_doc_cert_pem_bytes = read_test_file_bytes(
            'test_data/sii-crypto/AEC--76354771-K--33--170--SEQ-2-cert.pem',
        )

        cls.with_valid_signature = read_test_file_bytes(
            'test_data/sii-rtc/AEC--76354771-K--33--170--SEQ-2-canonicalized-c14n.xml',
        )
        cls.with_valid_signature_signed_data = read_test_file_bytes(
            'test_data/sii-rtc/AEC--76354771-K--33--170--SEQ-2-canonicalized-c14n-signed_data.xml',
        )
        cls.with_valid_signature_signed_xml = read_test_file_bytes(
            'test_data/sii-rtc/AEC--76354771-K--33--170--SEQ-2-canonicalized-c14n-signed_xml.xml',
        )
        cls.with_valid_signature_signature_xml = read_test_file_bytes(
            'test_data/sii-rtc/AEC--76354771-K--33--170--SEQ-2-canonicalized-c14n-signature_xml.xml',  # noqa: E501
        )

    def test_ok_external_trusted_cert(self) -> None:
        aec_xml_doc = parse_untrusted_xml(self.with_valid_signature)
        aec_xml = parse_aec_xml(aec_xml_doc)

        is_signature_verified = verify_aec_signature(aec_xml_doc=aec_xml_doc, aec_xml=aec_xml)

        self.assertTrue(is_signature_verified)

    def test_ok_for_bad_certificate_value(self) -> None:
        aec_xml_doc = parse_untrusted_xml(self.with_valid_signature)
        aec_xml_obj = parse_aec_xml(aec_xml_doc)

        aec_xml = dataclasses.replace(
            aec_xml_obj,
            signature_x509_cert_der=b'hello',
        )

        is_signature_verified = verify_aec_signature(aec_xml_doc=aec_xml_doc, aec_xml=aec_xml)

        self.assertIsNone(is_signature_verified)

    def test_fail_for_missing_certificate_value(self) -> None:
        aec_xml_doc = parse_untrusted_xml(self.with_valid_signature)
        aec_xml_obj = parse_aec_xml(aec_xml_doc)

        aec_xml = dataclasses.replace(
            aec_xml_obj,
            signature_value=None,
            signature_x509_cert_der=None,
        )

        with self.assertRaises(ValueError) as assert_raises_cm:
            verify_aec_signature(aec_xml_doc=aec_xml_doc, aec_xml=aec_xml)

        expected_error = "Field 'signature_x509_cert_der' can not be None."
        self.assertEqual(assert_raises_cm.exception.args, (expected_error,))
