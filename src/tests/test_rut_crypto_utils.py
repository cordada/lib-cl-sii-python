import unittest
from unittest.mock import Mock, patch

import cryptography.x509
from cryptography.hazmat.backends.openssl import backend as crypto_x509_backend

from cl_sii import rut
from cl_sii.libs.crypto_utils import load_der_x509_cert
from cl_sii.rut.crypto_utils import constants, get_subject_rut_from_certificate_pfx
from . import utils


class FunctionsTest(unittest.TestCase):
    def test_get_subject_rut_from_certificate_pfx_ok(self) -> None:
        cert_der_bytes = utils.read_test_file_bytes(
            'test_data/sii-crypto/DTE--76354771-K--33--170-cert.der'
        )

        x509_cert = load_der_x509_cert(cert_der_bytes)

        with patch.object(
            crypto_x509_backend,
            'load_key_and_certificates_from_pkcs12',
            Mock(return_value=(None, x509_cert, None)),
        ):
            pfx_file_bytes = b'hello'
            password = 'fake_password'
            subject_rut = get_subject_rut_from_certificate_pfx(
                pfx_file_bytes=pfx_file_bytes,
                password=password,
            )
            self.assertIsInstance(subject_rut, rut.Rut)
            self.assertEqual(subject_rut, rut.Rut('13185095-6'))

    def test_get_subject_rut_from_certificate_pfx_fails_if_rut_info_is_missing(self) -> None:
        cert_der_bytes = utils.read_test_file_bytes(
            'test_data/crypto/wildcard-google-com-cert.der',
        )

        x509_cert = load_der_x509_cert(cert_der_bytes)

        with patch.object(
            crypto_x509_backend,
            'load_key_and_certificates_from_pkcs12',
            Mock(return_value=(None, x509_cert, None)),
        ):
            pfx_file_bytes = b'hello'
            password = 'fake_password'
            with self.assertRaises(Exception) as cm:
                get_subject_rut_from_certificate_pfx(
                    pfx_file_bytes=pfx_file_bytes,
                    password=password,
                )
            self.assertEqual(cm.exception.args, ('Certificate has no RUT information',))

    def test_get_subject_rut_from_certificate_pfx_does_not_throw_attribute_error_if_has_object_without_type_id(  # noqa: E501
        self,
    ) -> None:
        cert_der_bytes = utils.read_test_file_bytes(
            'test_data/sii-crypto/DTE--76354771-K--33--170-cert.der'
        )
        x509_cert = load_der_x509_cert(cert_der_bytes)

        general_name_with_type_id = cryptography.x509.general_name.OtherName(
            type_id=constants.SII_CERT_TITULAR_RUT_OID,
            value=b'\x16\n17178452-2',
        )
        general_name_without_type_id = cryptography.x509.general_name.RFC822Name(
            value='test string',
        )
        general_names = cryptography.x509.extensions.GeneralNames(
            general_names=[general_name_without_type_id, general_name_with_type_id],
        )
        certificate_extension_value = cryptography.x509.extensions.SubjectAlternativeName(
            general_names=general_names,
        )
        certificate_extension = cryptography.x509.extensions.Extension(
            oid=constants.SII_CERT_TITULAR_RUT_OID,
            critical=False,
            value=certificate_extension_value,
        )

        with patch.object(
            crypto_x509_backend,
            'load_key_and_certificates_from_pkcs12',
            Mock(return_value=(None, x509_cert, None)),
        ), patch.object(
            x509_cert.extensions,
            'get_extension_for_class',
            Mock(return_value=certificate_extension),
        ):
            pfx_file_bytes = b'hello'
            password = 'fake_password'
            subject_rut = get_subject_rut_from_certificate_pfx(
                pfx_file_bytes=pfx_file_bytes,
                password=password,
            )
            self.assertIsInstance(subject_rut, rut.Rut)
            self.assertEqual(subject_rut, rut.Rut('17178452-2'))
