"""
XML utils
=========


XML (Digital) Signature
-----------------------

a.k.a. 'XMLDSig', 'XML-DSig', XML-Sig'

XML Signature [..] defines an XML syntax for digital signatures and is
defined in the W3C recommendation "XML Signature Syntax and Processing"
(``xmldsig-core``). Functionally, it has much in common with ``PKCS#7 ``
but is more extensible and geared towards signing XML documents.
It is used by various Web technologies such as SOAP, SAML, and others.

.. seealso::
    https://en.wikipedia.org/wiki/XML_Signature


"""
import io
import logging
import os
import xml.parsers.expat
import xml.parsers.expat.errors
from typing import IO, Optional, Tuple, Union

import defusedxml
import defusedxml.lxml
import lxml.etree
import signxml
import signxml.exceptions
from lxml.etree import ElementBase as XmlElement
from lxml.etree import XMLSchema as XmlSchema
from lxml.etree import (  # note: 'lxml.etree.ElementTree' is a **function**, not a class.  # noqa: E501
    _ElementTree as XmlElementTree,
)

from . import crypto_utils


logger = logging.getLogger(__name__)


XML_DSIG_NS_MAP = dict(
    ds='http://www.w3.org/2000/09/xmldsig#',
    dsig11='http://www.w3.org/2009/xmldsig11#',
    dsig2='http://www.w3.org/2010/xmldsig2#',
    ec='http://www.w3.org/2001/10/xml-exc-c14n#',
    dsig_more='http://www.w3.org/2001/04/xmldsig-more#',
    xenc='http://www.w3.org/2001/04/xmlenc#',
    xenc11='http://www.w3.org/2009/xmlenc11#',
)
"""
Mapping from XML namespace prefix to full name, for XML Signature.

Source:
``signxml.namespaces`` @ 16503242 (~ v2.6.0)
https://github.com/XML-Security/signxml/blob/16503242/signxml/__init__.py#L23-L31
"""


###############################################################################
# exceptions
###############################################################################


class BaseXmlParsingError(Exception):

    """
    Base class for all XML parsing errors.
    """


class XmlSyntaxError(BaseXmlParsingError):

    """
    The value to be parsed is syntactically invalid XML.

    It is also possible that some cases of maliciously constructed data are
    reported as syntactically invalid XML e.g. a "billion laughs" attack.

    """


class XmlFeatureForbidden(BaseXmlParsingError):

    """
    The parsed XML contains/uses a feature that is forbidden.

    Usually an XML feature is forbidden for security reasons, to prevent
    some attack vectors.

    .. seealso::
        https://docs.python.org/3/library/xml.html#xml-vulnerabilities

    """


class UnknownXmlParsingError(BaseXmlParsingError):

    """
    An unkwnown XML parsing error or for which there is no handling implementation.

    It is useful because the XML parsing process indirectly uses many
    (standard and 3rd party) libraries, some of them with native
    implementations and/or with a lot of obscure Python magic.

    """


class XmlSchemaDocValidationError(Exception):

    """
    XML document did not be validate against an XML schema.

    """


class XmlSignatureInvalid(Exception):

    """
    XML signature is invalid, for any reason.
    """


class XmlSignatureUnverified(XmlSignatureInvalid):

    """
    XML signature verification (i.e. digest validation) failed.

    This means the signature is not to be trusted.
    """


class XmlSignatureInvalidCertificate(XmlSignatureInvalid):

    """
    Certificate validation failed on XML signature processing.
    """


###############################################################################
# functions
###############################################################################


def parse_untrusted_xml(value: bytes) -> XmlElement:
    """
    Parse XML-encoded content in value.

    .. note::
        It is ok to use it for parsing untrusted or unauthenticated data.
        See https://docs.python.org/3/library/xml.html#xml-vulnerabilities

    .. warning::
        It is possible that for some cases of maliciously constructed data an
        ``XmlSyntaxError`` will be raised instead of a ``XmlFeatureForbidden``
        exception.

    :raises TypeError:
    :raises XmlSyntaxError: if it is not syntactically valid XML
    :raises XmlFeatureForbidden: if the parsed XML document contains/uses a
        feature that is forbidden
    :raises UnknownXmlParsingError: unkwnown XML parsing error or for which
        there is no handling implementation

    """
    # TODO: limit input max size (it might not be straightforward if value is a generator, which
    #   would be desirable).

    if not isinstance(value, bytes):
        raise TypeError("Value to be parsed as XML must be bytes.")

    # note: with this call, 'defusedxml' will
    # - create a custom parser (instance of 'lxml.etree.XMLParser'), which is what will
    #   fundamentally add safety to the parsing (e.g. using 'defusedxml.lxml.RestrictedElement'
    #   as a custom version of 'lxml.etree.ElementBase'),
    # - call the original 'lxml.etree.fromstring' (binary code),
    # - run 'defusedxml.lxml.check_docinfo'.

    # warning: do NOT change the exception handling order.
    try:

        xml_root_em = defusedxml.lxml.fromstring(
            text=value,
            parser=None,  # default: None (a custom one will be created)
            base_url=None,  # default: None
            forbid_dtd=False,  # default: False (allow Document Type Definition)
            forbid_entities=True,  # default: True (forbid Entity definitions/declarations)
        )  # type: XmlElement

    except (
        defusedxml.DTDForbidden,
        defusedxml.EntitiesForbidden,
        defusedxml.ExternalReferenceForbidden,
    ) as exc:
        # note: we'd rather use 'defusedxml.DefusedXmlException' but that would catch
        #   'defusedxml.NotSupportedError' as well

        raise XmlFeatureForbidden("XML uses or contains a forbidden feature.") from exc

    except lxml.etree.XMLSyntaxError as exc:
        # note: the MRO of this exception class is:
        # - XMLSyntaxError: "Syntax error while parsing an XML document."
        # - ParseError: "Syntax error while parsing an XML document."
        #   note: do not confuse it with the almost identically named 'lxml.etree.ParserError'
        #   ("Internal lxml parser error"), whose parent class *is not* 'LxmlSyntaxError'.
        # - LxmlSyntaxError: "Base class for all syntax errors."
        # - LxmlError: "Main exception base class for lxml. All other exceptions inherit from
        #   this one.
        # - lxml.etree.Error: "Common base class for all non-exit exceptions."

        # 'exc.msg' is a user-friendly error msg and includes the reference to line and column
        #   e.g. "Detected an entity reference loop, line 1, column 7".
        # Thus we do not need these attributes: (exc.position, exc.lineno, exc.offset)
        exc_msg = "XML syntax error. {}.".format(exc.msg)
        raise XmlSyntaxError(exc_msg) from exc

    except xml.parsers.expat.ExpatError as exc:
        # TODO: if this is reached it means we should improve this exception handler (even if
        #   it is just to raise the same exception with a different message) because
        #   it is a good idea to determine whether the source of the problem really is the
        #   XML-encoded content.

        # https://docs.python.org/3/library/pyexpat.html#expaterror-exceptions
        # https://docs.python.org/3/library/pyexpat.html#xml.parsers.expat.errors.messages
        # e.g.
        #   "unknown encoding"
        #   "mismatched tag"
        #   "parsing aborted"
        #   "out of memory"

        # For sanity crop the XML-encoded content to max 1 KiB (arbitrary value).
        log_msg = "Unexpected XML 'ExpatError' at line {} offset {}: {}. Content: %s".format(
            exc.lineno, exc.offset, xml.parsers.expat.errors.messages[exc.code]
        )
        logger.exception(log_msg, str(value[:1024]))

        exc_msg = "Unexpected error while parsing value as XML. Line {}, offset {}.".format(
            exc.lineno, exc.offset
        )
        raise UnknownXmlParsingError(exc_msg) from exc

    except lxml.etree.LxmlError as exc:
        # TODO: if this is reached it means we should add another exception handler (even if
        #   it is just to raise the same exception with the same message) because it is a good
        #   idea to determine whether the source of the problem really is the response content.

        # For sanity crop the XML-encoded content to max 1 KiB (arbitrary value).
        log_msg = "Unexpected 'LxmlError' that is not an 'XMLSyntaxError'. Content: %s"
        logger.exception(log_msg, str(value[:1024]))

        exc_msg = "Unexpected error while parsing value as XML."
        raise UnknownXmlParsingError(exc_msg) from exc

    except ValueError as exc:
        # TODO: if this is reached it means we should add another exception handler (even if
        #   it is just to raise the same exception with the same message) because it is a good
        #   idea to determine whether the source of the problem really is the response content.

        # For sanity crop the XML-encoded content to max 1 KiB (arbitrary value).
        log_msg = "Unexpected error while parsing value as XML. Content: %s"
        logger.exception(log_msg, str(value[:1024]))

        exc_msg = "Unexpected error while parsing value as XML."
        raise UnknownXmlParsingError(exc_msg) from exc

    return xml_root_em


def read_xml_schema(filename: str) -> XmlSchema:
    """
    Instantiate an XML schema object from a file.

    :raises ValueError: if there is no file at ``filename``

    """
    if os.path.exists(filename) and os.path.isfile(filename):
        return XmlSchema(file=filename)
    raise ValueError("XML schema file not found.", filename)


def validate_xml_doc(xml_schema: XmlSchema, xml_doc: XmlElement) -> None:
    """
    Validate ``xml_doc`` against XML schema ``xml_schema``.

    :raises XmlSchemaDocValidationError: if ``xml_doc`` did not be validate
        against ``xml_schema``

    """
    # There are several ways to validate 'xml_doc' according to an 'xml_schema'.
    #   Different calls and what happens if validation passes or fails:
    #   - xml_schema.assert_(xml_doc): nothign / raises 'AssertionError'
    #   - xml_schema.assertValid(xml_doc): nothing / raises 'DocumentInvalid'
    #   - xml_schema.validate(xml_doc): returns True / returns False

    try:
        xml_schema.assertValid(xml_doc)
    except lxml.etree.DocumentInvalid as exc:
        # note: 'exc.error_log' and 'xml_schema.error_log' are the same object
        #   (type 'lxml.etree._ListErrorLog').

        # TODO: advanced error details parsing, without leaking too much information.
        # xml_error_log = exc.error_log  # type: lxml.etree._ListErrorLog
        # last_xml_error = exc.error_log.last_error  # type: lxml.etree._LogEntry
        # last_xml_error_xml_doc_line = last_xml_error.line

        # TODO: does 'xml_schema.error_log' persist? is it necessary to clear it afterwards?
        #   `xml_schema._clear_error_log()`

        # Simplest and safest way to get the error message.
        # Error example:
        #   "Element 'DTE': No matching global declaration available for the validation root., line 2"  # noqa: E501
        validation_error_msg = str(exc)

        raise XmlSchemaDocValidationError(validation_error_msg) from exc


def write_xml_doc(xml_doc: XmlElement, output: IO[bytes]) -> None:
    """
    Write ``xml_doc`` to bytes stream ``output``.

    In this context, "write" means "serialize", so there are a number of
    observations on that regard:

    * Encoding will be preserved.
    * XML declaration (``<?xml ... ?>``) will be included.
    * Quoting of each XML declaration attribute's value may change
      i.e. from ``"`` to ``'`` or viceversa.
    * In self-closing tags, the whitespace between the last attribute
      and the closing (``/>``) may be removed e.g.
      ``<DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1" />`` to
      ``<DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"/>``
    * No pretty-print.

    For a temporary bytes stream in memory you may create a
    :class:`io.BytesIO` object.

    """
    # note: use `IO[X]` for arguments and `TextIO`/`BinaryIO` for return types (says GVR).
    #   https://github.com/python/typing/issues/518#issuecomment-350903120

    xml_etree: XmlElementTree = xml_doc.getroottree()

    # See:
    #   https://lxml.de/api/lxml.etree._ElementTree-class.html#write
    xml_etree.write(
        file=output,
        encoding=xml_etree.docinfo.encoding,
        # alternatives: 'xml', 'html', 'text' or 'c14n'
        method='xml',
        # note: include XML declaration (`<?xml ... ?>`).
        xml_declaration=True,
        pretty_print=False,
        # note: we are not sure what this does.
        # default: True.
        with_tail=True,
    )


def verify_xml_signature(
    xml_doc: XmlElement,
    trusted_x509_cert: Union[crypto_utils.X509Cert, crypto_utils._X509CertOpenSsl] = None,
    xml_verifier: Optional[signxml.XMLVerifier] = None,
    xml_verifier_supports_multiple_signatures: bool = False,
) -> Tuple[bytes, XmlElementTree, XmlElementTree]:
    """
    Verify the XML signature in ``xml_doc``.

    .. note::
        XML document with more than one signature is not supported.

    If the inputs are ok but the XML signature does not verify,
    raises :class:`XmlSignatureUnverified`.

    If ``trusted_x509_cert`` is None, it requires that the signature in
    ``xml_doc`` includes a a valid X.509 **certificate chain** that
    validates against the *known certificate authorities*.

    If ``trusted_x509_cert`` is given, it must be a **trusted** external
    X.509 certificate, and the verification will be of whether the XML
    signature in ``xml_doc`` was signed by ``trusted_x509_cert`` or not;
    thus **it overrides** any X.509 certificate information included
    in the signature.

    .. note::
        It is strongly recommended to validate ``xml_doc`` beforehand
        (against the corresponding XML schema, using :func:`validate_xml_doc`).

    :param xml_doc:
    :param trusted_x509_cert: a trusted external X.509 certificate, or None
    :param xml_verifier: Custom XML signature verifier. Use ``None`` for the
        default verifier.
    :param xml_verifier_supports_multiple_signatures: Set to ``True`` if
        ``xml_verifier`` is able to correctly verify XML documents that contain
        multiple signatures.
    :raises :class:`XmlSignatureUnverified`:
        signature did not verify
    :raises :class:`XmlSignatureInvalidCertificate`:
        certificate validation failed
    :raises :class:`XmlSignatureInvalid`:
        signature is invalid
    :raises :class:`XmlSchemaDocValidationError`:
        XML doc is not valid
    :raises :class:`ValueError`:

    """
    if not isinstance(xml_doc, XmlElement):
        raise TypeError("'xml_doc' must be an XML document/element.")

    use_default_xml_verifier = xml_verifier is None

    if use_default_xml_verifier and xml_verifier_supports_multiple_signatures:
        raise NotImplementedError(
            "Default XML signature verifier"
            " does not support XML documents with more than one signature."
        )

    n_signatures = (
        len(xml_doc.findall('.//ds:Signature', namespaces=XML_DSIG_NS_MAP))
        + len(xml_doc.findall('.//dsig11:Signature', namespaces=XML_DSIG_NS_MAP))
        + len(xml_doc.findall('.//dsig2:Signature', namespaces=XML_DSIG_NS_MAP))
    )

    if n_signatures > 1 and not xml_verifier_supports_multiple_signatures:
        raise NotImplementedError("XML document with more than one signature is not supported.")

    if use_default_xml_verifier:
        xml_verifier = signxml.XMLVerifier()

        # Workaround for breaking change in signxml 2.10.0 and 2.10.1:
        # (See https://github.com/XML-Security/signxml/blob/v2.10.1/Changes.rst)
        xml_verifier.excise_empty_xmlns_declarations = True

    if not isinstance(xml_verifier, signxml.XMLVerifier):
        raise TypeError(
            "'xml_verifier' must be an instance of 'signxml.XMLVerifier' or of a subclass of it."
        )

    if isinstance(trusted_x509_cert, crypto_utils._X509CertOpenSsl):
        trusted_x509_cert_open_ssl = trusted_x509_cert
    elif isinstance(trusted_x509_cert, crypto_utils.X509Cert):
        trusted_x509_cert_open_ssl = crypto_utils._X509CertOpenSsl.from_cryptography(
            trusted_x509_cert
        )
    elif trusted_x509_cert is None:
        trusted_x509_cert_open_ssl = None
    else:
        # A 'crypto_utils._X509CertOpenSsl' is ok but we prefer 'crypto_utils.X509Cert'.
        raise TypeError("'trusted_x509_cert' must be a 'crypto_utils.X509Cert' instance, or None.")

    # warning: performance issue.
    # note: 'signxml.XMLVerifier.verify()' calls 'signxml.util.XMLProcessor.get_root()',
    #   which converts the data to string, and then reparses it using the same function we use
    #   in 'parse_untrusted_xml()' ('defusedxml.lxml.fromstring'), but without all the precautions
    #   we have there. See:
    #      https://github.com/XML-Security/signxml/blob/v2.6.0/signxml/util/__init__.py#L141-L151
    #   Considering that, we'd rather write to bytes ourselves and control the process.
    f = io.BytesIO()
    write_xml_doc(xml_doc, f)
    tmp_bytes = f.getvalue()

    try:
        # note: by passing 'x509_cert' we override any X.509 certificate information supplied
        #   by the signature itself.

        # note: when an X509Data element is present in the signature and used for verification, but
        #   a KeyValue element is also present, there is an ambiguity and a security hazard because
        #   the public key used to sign the document is already encoded in the certificate (which is
        #   in X509Data), so the verifier must either ignore KeyValue or ensure that it matches what
        #   is in the certificate. SignXML does not perform that validation and throws an
        #   'InvalidInput' error instead.
        #
        #   SII's schema for XML signatures requires both elements to be present, which forces us to
        #   enable 'ignore_ambiguous_key_info' to bypass the error and validate the signature using
        #   X509Data only.
        #
        #   Source:
        #   https://github.com/XML-Security/signxml/commit/ef15da8dbb904f1dedfdd210ae3e0df5da535612
        result: signxml.VerifyResult = xml_verifier.verify(
            data=tmp_bytes,
            require_x509=True,
            x509_cert=trusted_x509_cert_open_ssl,
            ignore_ambiguous_key_info=True,
        )

    except signxml.exceptions.InvalidDigest as exc:
        # warning: catch before 'InvalidSignature' (it is the parent of 'InvalidDigest').
        raise XmlSignatureUnverified(str(exc)) from exc

    except signxml.exceptions.InvalidCertificate as exc:
        # warning: catch before 'InvalidSignature' (it is the parent of 'InvalidCertificate').
        raise XmlSignatureInvalidCertificate(str(exc)) from exc

    except signxml.exceptions.InvalidSignature as exc:
        # XML signature is invalid, for any reason.
        raise XmlSignatureInvalid(str(exc)) from exc

    except signxml.exceptions.InvalidInput as exc:
        raise ValueError("Invalid input.", str(exc)) from exc

    except lxml.etree.DocumentInvalid as exc:
        # Simplest and safest way to get the error message (see 'validate_xml_doc()').
        # Error example:
        #   "Element '{http://www.w3.org/2000/09/xmldsig#}X509Certificate': '\nabc\n' is not a
        #   valid value of the atomic type 'xs:base64Binary'., line 30"
        validation_error_msg = str(exc)
        raise XmlSchemaDocValidationError(validation_error_msg) from exc

    return result.signed_data, result.signed_xml, result.signature_xml
