from __future__ import annotations

import logging
from typing import Any, ClassVar, Optional

import signxml

from cl_sii.dte.parse import DTE_XMLNS_MAP
from cl_sii.libs import crypto_utils, xml_utils
from .data_models_aec import AecXml


logger = logging.getLogger(__name__)


class AecXMLVerifier(signxml.XMLVerifier):
    """
    Custom XML Signature Verifier for AECs.
    """

    AEC_XML_ELEMENT_TAG: ClassVar[str] = '{{{namespace}}}{tag}'.format(
        namespace=DTE_XMLNS_MAP['sii-dte'],
        tag='AEC',
    )

    def _get_signature(self, root: Any) -> object:
        if root.tag != self.AEC_XML_ELEMENT_TAG:
            raise ValueError(
                f'Only XML element {self.AEC_XML_ELEMENT_TAG!r} is supported. Found: {root.tag!r}',
            )

        if root.tag == signxml.ds_tag("Signature"):
            return root
        else:
            return self._find(root, "Signature", anywhere=False)


###############################################################################
# functions
###############################################################################


def verify_aec_signature(
    aec_xml_doc: xml_utils.XmlElement,
    aec_xml: AecXml,
) -> Optional[bool]:
    """
    Verify signature of AEC XML document ``aec_xml_doc``.

    :param aec_xml_doc: An AEC XML document, as returned by ``xml_utils.parse_untrusted_xml()``.
    :param aec_xml: An instance of ``data_models_aec.AecXml`` with the data in the "cesión"'s
        AEC XML document parsed from `aec_xml_doc` by ``parse_aec.parse_aec_xml``.
    :raises ValueError: If the attribute `signature_x509_cert_der` of the AecXml is None.
    :raises Exception: on unrecoverable errors
    """
    signature_verified: Optional[bool]
    signature_x509_cert: Optional[crypto_utils.X509Cert]

    if aec_xml.signature_x509_cert_der is None:
        raise ValueError("Field 'signature_x509_cert_der' can not be None.")

    try:
        signature_x509_cert = crypto_utils.load_der_x509_cert(
            aec_xml.signature_x509_cert_der,
        )
    except ValueError:
        signature_verified = None
        logger.debug(
            "The X.509 certificate could not be loaded from AEC's digital "
            "signature's DER-encoded X.509 certificate."
        )
        return signature_verified

    try:
        aec_xml_verifier = AecXMLVerifier()

        # Workaround for breaking change in signxml 2.10.0 and 2.10.1:
        # (See https://github.com/XML-Security/signxml/blob/v2.10.1/Changes.rst)
        aec_xml_verifier.excise_empty_xmlns_declarations = True

        xml_utils.verify_xml_signature(
            aec_xml_doc,
            trusted_x509_cert=signature_x509_cert,
            xml_verifier=aec_xml_verifier,
            xml_verifier_supports_multiple_signatures=True,
        )
    except xml_utils.XmlSignatureUnverified:
        signature_verified = False
        logger.debug("AEC's digital signature did not verify")
    except xml_utils.XmlSignatureInvalid:
        signature_verified = False
        logger.debug("AEC's digital signature is invalid")
    except Exception:
        signature_verified = None
        logger.exception(
            "Unexpected error when trying to verify digital signature of XML document. "
            "X509 certificate: %s",
            signature_x509_cert,
        )
    else:
        signature_verified = True

    return signature_verified
