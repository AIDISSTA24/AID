import uuid

from lxml import etree
from lxml.builder import ElementMaker
from zeep import ns
from zeep.plugins import Plugin
from zeep.wsdl.utils import get_or_create_header

WSA = ElementMaker(namespace=ns.WSA, nsmap={"wsa": ns.WSA})


class WsAddressingIfMissingPlugin(Plugin):
    nsmap = {"wsa": ns.WSA}

    def __init__(self, address_url: str = None):
        self.address_url = address_url

    def egress(self, envelope, http_headers, operation, binding_options):
        """Apply the ws-addressing headers to the given envelope."""
        header = get_or_create_header(envelope)
        for elem in header:
            if (elem.prefix or "").startswith("wsa"):
                # WSA header already exists
                return envelope, http_headers

        wsa_action = operation.abstract.wsa_action
        if not wsa_action:
            wsa_action = operation.soapaction

        headers = [
            WSA.Action(wsa_action),
            WSA.MessageID("urn:uuid:" + str(uuid.uuid4())),
            WSA.To(self.address_url or binding_options["address"]),
        ]
        header.extend(headers)

        # the top_nsmap kwarg was added in lxml 3.5.0
        if etree.LXML_VERSION[:2] >= (3, 5):
            etree.cleanup_namespaces(
                header, keep_ns_prefixes=header.nsmap, top_nsmap=self.nsmap
            )
        else:
            etree.cleanup_namespaces(header)
        return envelope, http_headers
