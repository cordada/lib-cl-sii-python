import unittest

import lxml.etree

from cl_sii.libs.xml_utils import (  # noqa: F401
    XmlSyntaxError, XmlFeatureForbidden,
    parse_untrusted_xml, read_xml_schema, validate_xml_doc, write_xml_doc,
)

from .utils import read_test_file_bytes


class FunctionParseUntrustedXmlTests(unittest.TestCase):

    def test_parse_untrusted_xml_valid(self) -> None:
        value = (
            b'<root>\n'
            b'   <element key="value">text</element>\n'
            b'   <element>text</element>tail\n'
            b'   <empty-element/>\n'
            b'</root>')
        xml = parse_untrusted_xml(value)
        self.assertIsInstance(xml, lxml.etree.ElementBase)
        # print(xml)
        self.assertEqual(
            lxml.etree.tostring(xml, pretty_print=False),
            value)

    def test_bytes_text(self) -> None:
        value = b'not xml'  # type: ignore
        with self.assertRaises(XmlSyntaxError) as cm:
            parse_untrusted_xml(value)

        self.assertSequenceEqual(
            cm.exception.args,
            ("XML syntax error. Start tag expected, '<' not found, line 1, column 1.", )
        )

    def test_attack_billion_laughs_1(self) -> None:
        value = read_test_file_bytes('test_data/xml/attacks/billion-laughs-1.xml')
        with self.assertRaises(XmlSyntaxError) as cm:
            parse_untrusted_xml(value)

        self.assertSequenceEqual(
            cm.exception.args,
            ("XML syntax error. Detected an entity reference loop, line 1, column 7.", )
        )

    def test_attack_billion_laughs_2(self) -> None:
        value = read_test_file_bytes('test_data/xml/attacks/billion-laughs-2.xml')
        with self.assertRaises(XmlSyntaxError) as cm:
            parse_untrusted_xml(value)

        self.assertSequenceEqual(
            cm.exception.args,
            ("XML syntax error. Detected an entity reference loop, line 1, column 4.", )
        )

    def test_attack_quadratic_blowup(self) -> None:
        value = read_test_file_bytes('test_data/xml/attacks/quadratic-blowup-entity-expansion.xml')
        with self.assertRaises(XmlFeatureForbidden) as cm:
            parse_untrusted_xml(value)

        self.assertSequenceEqual(
            cm.exception.args,
            ("XML uses or contains a forbidden feature.", )
        )

    def test_attack_external_entity_expansion_remote(self) -> None:
        value = read_test_file_bytes('test_data/xml/attacks/external-entity-expansion-remote.xml')
        with self.assertRaises(XmlFeatureForbidden) as cm:
            parse_untrusted_xml(value)

        self.assertSequenceEqual(
            cm.exception.args,
            ("XML uses or contains a forbidden feature.", )
        )

    def test_type_error(self) -> None:
        value = 1  # type: ignore
        with self.assertRaises(TypeError) as cm:
            parse_untrusted_xml(value)

        self.assertSequenceEqual(
            cm.exception.args,
            ("Value to be parsed as XML must be bytes.", )
        )


class FunctionReadXmlSchemaTest(unittest.TestCase):

    # TODO: implement

    pass


class FunctionValidateXmlDocTest(unittest.TestCase):

    # TODO: implement

    pass


class FunctionWriteXmlDocTest(unittest.TestCase):

    # TODO: implement for function 'write_xml_doc'. Consider each of the "observations".
    pass
