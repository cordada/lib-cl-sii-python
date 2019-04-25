from typing import Union

import cryptography.x509
import signxml.util
from cryptography.hazmat.backends.openssl import backend as _crypto_x509_backend
from cryptography.x509 import Certificate as X509Cert
from OpenSSL.crypto import X509 as _X509CertOpenSsl  # noqa: F401


def load_pem_x509_cert(pem_value: Union[str, bytes]) -> X509Cert:
    """
    Load an X.509 certificate from a PEM-formatted value.

    .. seealso::
        https://cryptography.io/en/latest/faq/#why-can-t-i-import-my-pem-file

    :raises TypeError:
    :raises ValueError:

    """
    if isinstance(pem_value, str):
        pem_value_bytes = pem_value.encode('ascii')
    elif isinstance(pem_value, bytes):
        pem_value_bytes = pem_value
    else:
        raise TypeError("Value must be str or bytes.")

    mod_pem_value_bytes = add_pem_cert_header_footer(pem_value_bytes)
    try:
        x509_cert = cryptography.x509.load_pem_x509_certificate(
            data=mod_pem_value_bytes,
            backend=_crypto_x509_backend)
    except ValueError:
        # e.g.
        #   "Unable to load certificate. See
        #   https://cryptography.io/en/latest/faq/#why-can-t-i-import-my-pem-file for more details."
        raise

    return x509_cert


def add_pem_cert_header_footer(pem_cert: bytes) -> bytes:
    """
    Add certificate PEM header and footer (if not already present).
    """
    pem_value_str = pem_cert.decode('ascii')
    # note: it would be great if 'add_pem_header' did not forcefully convert bytes to str.
    mod_pem_value_str = signxml.util.add_pem_header(pem_value_str)
    mod_pem_value: bytes = mod_pem_value_str.encode('ascii')
    return mod_pem_value


def remove_pem_cert_header_footer(pem_cert: bytes) -> bytes:
    """
    Remove certificate PEM header and footer (if they are present).
    """
    pem_value_str = pem_cert.decode('ascii')
    # note: it would be great if 'strip_pem_header' did not expect input to be a str.
    mod_pem_value_str = signxml.util.strip_pem_header(pem_value_str)
    mod_pem_value: bytes = mod_pem_value_str.encode('ascii').strip()
    return mod_pem_value
