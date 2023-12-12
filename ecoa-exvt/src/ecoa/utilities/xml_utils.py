# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

""" xml_utils module """
from xml.etree import ElementTree
from xml.dom import minidom
from lxml import etree as lxmlEtree
from .logs import info, warning, critical
import os


def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem)

    parser = lxmlEtree.XMLParser(remove_blank_text=True)
    reparsed = document_root = lxmlEtree.XML(rough_string, parser=parser)

    return lxmlEtree.tostring(reparsed, pretty_print=True,
                                        with_tail=True,
                                        encoding="utf-8",
                                        xml_declaration=True)


def validate_XML_file(xml_filename, xsd_filename):
    """ validate a xml file with xsd file

    Return:
        (int) :
            * -1 if xml file is not validated
            * 0 if xsd cannot be validate
            * 1 if xml file is validated
    """

    try:

        info("parsing file: "+xml_filename)
        XSD_file = lxmlEtree.parse(xsd_filename)
        XML_file = lxmlEtree.parse(xml_filename)
        schema = lxmlEtree.XMLSchema(XSD_file)

        if not schema.validate(XML_file):
            critical("Configuration file %s is not valid" % xml_filename)
            for error in schema.error_log:
                critical("ERROR ON LINE %s: %s" % (error.line, error.message.encode("utf-8")))
            return -1

    except lxmlEtree.ParseError as e:
        critical("Invalid format XML for "+xml_filename+"\n"+str(e))
        return -1
    except Exception as e:
        warning("Cannot validate XML for "+xml_filename+"\n"+str(e))
        return 0

    return 1


def write_xml_file(filename, xml_root, force_write=True):
    if not force_write and os.path.isfile(filename):
        # don't overwritten the existing file
        info("File '%s' already exist. Not overwritten."%filename)
        return

    if os.path.dirname(filename) != "":
        os.makedirs(os.path.dirname(filename), exist_ok=True)

    f = open(filename, 'wb')
    f.write(prettify(xml_root))
    f.flush()
    f.close()
