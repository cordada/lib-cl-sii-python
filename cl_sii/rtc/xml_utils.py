from __future__ import annotations

from typing import Any, ClassVar

import signxml

from cl_sii.dte.parse import DTE_XMLNS_MAP


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
