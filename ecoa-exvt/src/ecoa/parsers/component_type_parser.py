# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

import os
from xml.etree.ElementTree import ElementTree
from ..models.component_type import Component_Type
from ..utilities.namespaces import NameSpaces, CSA, ECOS_SCA
from ..utilities.logs import debug, error, info, warning
from ..utilities.xml_utils import validate_XML_file


def parse_component_types(xsd_directory, comp_files, component_types, libraries):
    for comp_filename in sorted(comp_files):
        parse_component_type(xsd_directory, comp_filename, component_types, libraries)

    for n, t in component_types.items():
        debug(t[0].to_string())
        debug("Name: %s %d %d %d" % \
             (n, t[0].get_id(), len(t[0].services), len(t[0].references)))

    return True


def parse_component_type(xsd_directory, comp_filename, component_types, libraries):
    comp_name = str.replace(os.path.basename(comp_filename), ".componentType", '')

    if comp_name in component_types:
        info("component type %s already parsed" % (comp_name))
        return False

    if os.path.exists(comp_filename) is False:
        error("component type file '%s' does not exist" % (comp_filename))
        return False

    tree = ElementTree()
    if (validate_XML_file(comp_filename, os.path.join(xsd_directory, "Schemas_ecoa", "sca",
                                                    "sca-1.1-cd06-subset-2.0.xsd")) == -1):
        return False

    tree.parse(comp_filename)

    component_type = Component_Type(comp_name)

    socket_number = 1  # first socket is for connection with father processus
    for s in tree.iterfind(CSA + "service"):
        name = s.get("name")
        for i in s.iterfind(ECOS_SCA + "interface"):
            syntax = i.get("syntax")
            qos = i.get("qos")
        component_type.add_service(name, syntax, socket_number, qos)
        socket_number += 1
    socket_number = 0
    for ref in tree.iterfind(CSA + "reference"):
        name = ref.get("name")
        for i in ref.iterfind(ECOS_SCA + "interface"):
            syntax = i.get("syntax")
            qos = i.get("qos")
        component_type.add_reference(name, syntax, socket_number, qos)
        socket_number += 1

    for proper in tree.iterfind(CSA + "property"):
        pname = proper.get("name")
        ptype = proper.get(ECOS_SCA + "type")
        component_type.add_property(pname, ptype, libraries)

    # Store a tuple to keep the parser
    component_types[comp_name] = (component_type, tree)

    return True


def check_component_types(component_types, service_definitions, libraries):
    ret_val = True

    # check if service or refecrence syntaxes exist
    for comp_type,_ in component_types.values():
        for serv_ref in comp_type.services + comp_type.references:
            if serv_ref.syntax not in service_definitions:
                error("in component_type '"+comp_type.name+"', reference or service '"+serv_ref.name+"'' has an unkown syntax '"+ serv_ref.syntax+"'")
                ret_val=False

    # Check if property types exist
    for comp_type,_ in component_types.values():
        for pty in comp_type.properties.values():
            pty_type_lib, pty_type_name = pty.type.split(':')

            if pty_type_lib not in libraries \
                or not libraries[pty_type_lib][0].is_datatype_defined(pty_type_name):
                    warning("in component_type '"+comp_type.name+"', property '"+pty.name+"' uses an unkown type '"+pty.type+"'")

    return ret_val
