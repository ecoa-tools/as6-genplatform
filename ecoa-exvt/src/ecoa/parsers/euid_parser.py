# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

import os
from xml.etree.ElementTree import ElementTree
from ..utilities.logs import error, warning
from ..utilities.xml_utils import validate_XML_file
from ..utilities.namespaces import ECOS_UID

def parse_all_EUID(xsd_directory, euid_files, IDs):
    for euid_file in euid_files:
        if os.path.exists(euid_file) is False:
            error("EUID File '%s' does not exist" % (euid_file))
            return False

        if validate_XML_file(euid_file, xsd_directory + "/Schemas_ecoa/ecoa-uid-2.0.xsd") == -1:
            return False

        parse_EUID_not_unique(euid_file, IDs)
    return True

def parse_EUID(filename, IDs):

    if os.path.exists(filename) is False:
        error("EUID File '%s' does not exist" % (filename))

    tree = ElementTree()
    tree.parse(filename)

    already_used_ids = list(IDs.values())
    for id_node in tree.iterfind(ECOS_UID+"ID"):
        key = id_node.get("key")
        value = id_node.get("value")

        if key in IDs:
            error("Id '%s' in file '%s' already exists" % (key, filename))
        else:
            if value in already_used_ids:
                warning("Id '%s in file '%s', value '%s' is already used"% (key, filename, value))
            IDs[key] = value
            already_used_ids.append(value)

def parse_EUID_not_unique(filename, IDs):
    if os.path.exists(filename) is False:
        error("EUID File '%s' does not exist" % (filename))
        return

    tree = ElementTree()
    tree.parse(filename)

    for id_node in tree.iterfind(ECOS_UID+"ID"):
        key = id_node.get("key")
        value = id_node.get("value")
        IDs[key] = value
