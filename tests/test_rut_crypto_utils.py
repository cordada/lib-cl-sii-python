import unittest
from unittest.mock import Mock, patch

from cryptography.hazmat.backends.openssl import backend as crypto_x509_backend

from cl_sii import rut
from cl_sii.libs.crypto_utils import load_der_x509_cert
from cl_sii.rut.crypto_utils import get_subject_rut_from_certificate_pfx
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
            'test_data/crypto/wildcard-google-com-cert.der'
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
