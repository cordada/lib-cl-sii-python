from __future__ import annotations

import io
import unittest

from cl_sii.libs.crypto_utils import load_pem_x509_cert
from cl_sii.libs.xml_utils import parse_untrusted_xml, verify_xml_signature, write_xml_doc
from cl_sii.rtc.xml_utils import AecXMLVerifier

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
