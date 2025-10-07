"""
Crypto utils
============


DER and PEM
-----------

Best answer to the
`StackOverflow question <https://stackoverflow.com/a/22743616>`_
"What are the differences between .pem, .cer and .der?".

Best answer to the
`ServerFault question <https://https://serverfault.com/a/9717>`_.
"What is a Pem file and how does it differ from other OpenSSL Generated Key File Formats?".


DER
--------

DER stands for "Distinguished Encoding Rules".

> A way to encode ASN.1 syntax in binary.

> The parent format of PEM. It's useful to think of it as a binary version
> of the base64-encoded PEM file.

PEM
--------

PEM stands for "Privacy Enhanced Mail".

> A failed method for secure email but the container format it used lives on,
> and is a base64 translation of the x509 ASN.1 keys.

> In the case that it encodes a certificate it would simply contain the
> base64 encoding of the DER certificate [plus the header and footer].

PKCS12
--------

PKCS12 stands for "Public Key Cryptography Standard #12".

> […] a binary format described in RFC 7292. It can contain certificates, keys, and more.
> PKCS12 files commonly have a `pfx` or `p12` file suffix.
"""

__all__ = [
    'X509Cert',
    '_X509CertOpenSsl',
]

import base64
from datetime import datetime
from typing import Optional, Union

import cryptography.hazmat.backends.openssl.backend as _crypto_x509_backend
import cryptography.hazmat.primitives.serialization.pkcs12
import cryptography.x509
import signxml.util
from cryptography.x509 import Certificate as X509Cert
from OpenSSL.crypto import X509 as _X509CertOpenSsl

from . import encoding_utils


def load_der_x509_cert(der_value: bytes) -> X509Cert:
    """
    Load an X.509 certificate from DER-encoded certificate data.

    :raises TypeError:
    :raises ValueError:

    """
    if not isinstance(der_value, bytes):
        raise TypeError("Value must be bytes.")

    try:
        x509_cert = cryptography.x509.load_der_x509_certificate(
            data=der_value,
            backend=_crypto_x509_backend,
        )
    except ValueError:
        # e.g.
        #   "Unable to load certificate"
        raise

    return x509_cert


def load_pem_x509_cert(pem_value: Union[str, bytes]) -> X509Cert:
    """
    Load an X.509 certificate from PEM-encoded certificate data.

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
            backend=_crypto_x509_backend,
        )
    except ValueError:
        # e.g.
        #   "Unable to load certificate. See
        #   https://cryptography.io/en/latest/faq/#why-can-t-i-import-my-pem-file for more details."
        raise

    return x509_cert


def x509_cert_der_to_pem(der_value: bytes) -> bytes:
    """
    Convert an X.509 certificate DER-encoded data to PEM-encoded.

    .. warning::
        It does not validate that ``der_value`` corresponds to an X.509 cert.

    :raises TypeError:

    """
    if not isinstance(der_value, bytes):
        raise TypeError("Value must be bytes.")

    pem_value = base64.standard_b64encode(der_value)
    mod_pem_value = add_pem_cert_header_footer(pem_value)

    return mod_pem_value.strip()


def x509_cert_pem_to_der(pem_value: bytes) -> bytes:
    """
    Convert an X.509 certificate PEM-encoded data to DER-encoded.

    .. warning::
        It does not validate that ``pem_value`` corresponds to an X.509 cert.

    :raises TypeError:
    :raises ValueError:

    """
    if not isinstance(pem_value, bytes):
        raise TypeError("Value must be bytes.")

    mod_pem_value = remove_pem_cert_header_footer(pem_value)
    der_value = encoding_utils.decode_base64_strict(mod_pem_value)

    return der_value.strip()


def add_pem_cert_header_footer(pem_cert: bytes) -> bytes:
    """
    Add certificate PEM header and footer (if not already present).
    """
    pem_value_str = pem_cert.decode('ascii')
    # note: it would be great if 'add_pem_header' did not forcefully convert bytes to str.
    mod_pem_value: bytes = signxml.util.add_pem_header(pem_value_str)
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


def load_pfx_x509_cert(pfx_value: bytes, password: Union[bytes, str, None]) -> Optional[X509Cert]:
    """
    Load an X.509 certificate from PKCS12-encoded data.

    :raises TypeError:
    :raises ValueError:
    """
    if isinstance(password, str):
        password = password.encode()

    try:
        p12 = cryptography.hazmat.primitives.serialization.pkcs12.load_pkcs12(
            data=pfx_value, password=password
        )
    except TypeError:
        # Examples:
        # - "TypeError: argument 'data': a bytes-like object is required, not 'NoneType'"
        # - "argument 'password': from_buffer() cannot return the address of a unicode object"
        raise
    except ValueError:
        # Examples:
        # - "Invalid password or PKCS12 data"
        # - "Could not deserialize PKCS12 data"
        raise

    pkcs12_cert = p12.cert
    x509_cert = pkcs12_cert.certificate if pkcs12_cert is not None else None
    return x509_cert


# Aliases for `load_pfx_x509_cert()`:
load_pkcs12_x509_cert = load_pfx_x509_cert
load_p12_x509_cert = load_pfx_x509_cert


def get_expiration_date_from_x509_certificate(certificate: X509Cert) -> datetime:
    """
    Return the expiration date-time of a digital certificate.

    :param certificate: X.509 certificate
    """
    cert_expires_at = certificate.not_valid_after_utc
    return cert_expires_at


def get_expiration_date_from_pfx_x509_certificate(
    pfx_file: bytes, password: Optional[str]
) -> Optional[datetime]:
    """
    Return the expiration date-time of a digital certificate. If the PKCS12 file
    does not contain a X.509 certificate, return ``None``.

    :param pfx_file: X.509 certificate in PKCS12 format
    :param password: (Optional) The password to use to decrypt the certificate.
    """
    if (cert_x509 := load_pfx_x509_cert(pfx_value=pfx_file, password=password)) is not None:
        return get_expiration_date_from_x509_certificate(cert_x509)
    else:
        return None
