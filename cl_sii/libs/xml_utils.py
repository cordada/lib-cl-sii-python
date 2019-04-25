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
import logging
import os
from typing import IO

import defusedxml
import defusedxml.lxml
import lxml.etree
import xml.parsers.expat
import xml.parsers.expat.errors
from lxml.etree import ElementBase as XmlElement  # noqa: F401
# note: 'lxml.etree.ElementTree' is a **function**, not a class.
from lxml.etree import _ElementTree as XmlElementTree  # noqa: F401
from lxml.etree import XMLSchema as XmlSchema  # noqa: F401


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
            parser=None,           # default: None (a custom one will be created)
            base_url=None,         # default: None
            forbid_dtd=False,      # default: False (allow Document Type Definition)
            forbid_entities=True,  # default: True (forbid Entity definitions/declarations)
        )  # type: XmlElement

    except (defusedxml.DTDForbidden,
            defusedxml.EntitiesForbidden,
            defusedxml.ExternalReferenceForbidden) as exc:
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
            exc.lineno, exc.offset, xml.parsers.expat.errors.messages[exc.code])
        logger.exception(log_msg, str(value[:1024]))

        exc_msg = "Unexpected error while parsing value as XML. Line {}, offset {}.".format(
            exc.lineno, exc.offset)
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
