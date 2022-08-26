import re
from typing import Optional

import cryptography
import cryptography.x509
from cryptography.hazmat.backends.openssl import backend as crypto_x509_backend

from . import Rut, constants


def get_subject_rut_from_certificate_pfx(pfx_file_bytes: bytes, password: Optional[str]) -> Rut:
    """
    Return the Chilean RUT stored in a digital certificate.

    Original source URL: https://github.com/fyntex/fd-cl-data/blob/cfd5a716fb9b2cbd8a03fca1bacfd1b844b1337f/fd_cl_data/apps/sii_auth/models/sii_auth_credential.py#L701-L745  # noqa: E501

    :param pfx_file_bytes: Digital certificate in PKCS12 format
    :param password: (Optional) The password to use to decrypt the PKCS12 file
    """
    (
        private_key,
        x509_cert,
        additional_certs,
    ) = crypto_x509_backend.load_key_and_certificates_from_pkcs12(
        data=pfx_file_bytes,
        password=password.encode() if password is not None else None,
    )
    # https://cryptography.io/en/latest/hazmat/primitives/asymmetric/serialization/#cryptography.hazmat.primitives.serialization.pkcs12.load_key_and_certificates  # noqa: E501

    assert x509_cert is not None

    subject_alt_name_ext = x509_cert.extensions.get_extension_for_class(
        cryptography.x509.extensions.SubjectAlternativeName,
    )

    # Search for the RUT in the certificate.
    try:
        results = [
            x.value
            for x in subject_alt_name_ext.value._general_names
            if hasattr(x, 'type_id') and x.type_id == constants.SII_CERT_TITULAR_RUT_OID
        ]
    except AttributeError as exc:
        raise Exception(f'Malformed certificate extension: {subject_alt_name_ext.oid}') from exc

    if not results:
        raise Exception('Certificate has no RUT information')
    elif len(results) > 1:
        raise Exception(f'len(results) == {len(results)}')

    subject_rut_raw: bytes = results[0]
    subject_rut = re.sub(r'[^0-9-]', '', subject_rut_raw.decode('utf-8'))

    return Rut(subject_rut)
