# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

import os

from xml.etree.ElementTree import ElementTree
from ..models.service_definition import Service_Definition
from ..utilities.namespaces import ECOS_IF
from ..models.operation_type import Parameter
from ..utilities.xml_utils import validate_XML_file
from ..utilities.logs import debug, error


def is_complex_type(libraries, type_name):
    for l, _ in libraries.values():
        start = type_name.find(':')
        if l.is_datatype_defined(type_name[start + 1:]):
            return l.get_data_type(type_name[start + 1:]).is_complex_type()
    return False

#
# Function: parse_service_definition
#
# Parse one given service definition
#
def parse_service_definition(xsd_directory, filename, service_definitions, service_syntax, libraries):
    if os.path.exists(filename) is False:
        error("File '%s' does not exist" % (filename))
        return False
    tree = ElementTree()
    if (validate_XML_file(filename, xsd_directory
                              + "/Schemas_ecoa/ecoa-interface-2.0.xsd") == -1):
        return False

    tree.parse(filename)

    service_definition = Service_Definition(service_syntax)

    for ops in tree.iterfind(ECOS_IF + "operations"):
        for d in ops.iterfind(ECOS_IF + "data"):
            on = d.get("name")
            ot = d.get("type")
            if ot in libraries['ECOA'][0].datatypes2 and "ECOA" not in ot:
                ot = 'ECOA:' + ot
            is_complex = is_complex_type(libraries, ot)

            service_definition.add_operation(on, "DATA", ot, [Parameter("data", ot, "input", is_complex)], [])

        for rr in ops.iterfind(ECOS_IF + "requestresponse"):
            on = rr.get("name")
            oinputs = []
            for i in rr.iterfind(ECOS_IF + "input"):
                iname = i.get("name")
                itype = i.get("type")
                i_is_complex = is_complex_type(libraries, itype)
                oinputs.append(Parameter(iname, itype, "input", i_is_complex))
            ooutputs = []
            for o in rr.iterfind(ECOS_IF + "output"):
                oname = o.get("name")
                otype = o.get("type")
                ooutputs.append(Parameter(oname, otype, "output"))
            service_definition.add_operation(on, "RR", "", oinputs, ooutputs)

        for e in ops.iterfind(ECOS_IF + "event"):
            od = e.get("direction")
            on = e.get("name")
            oinputs = []
            for i in e.iterfind(ECOS_IF + "input"):
                iname = i.get("name")
                itype = i.get("type")
                i_is_complex = is_complex_type(libraries, itype)
                oinputs.append(Parameter(iname, itype, "input", i_is_complex))
            if od == "RECEIVED_BY_PROVIDER":
                service_definition.add_operation(on, "CMD", "", oinputs, [])
            elif od == "SENT_BY_PROVIDER":
                service_definition.add_operation(on, "NOTIFY", "", oinputs, [])
            else:
                error("Unknown direction for event %s in service definition %s" % (on, service_syntax))

    for l in tree.iterfind(ECOS_IF + "use"):
        ln = l.get("library")
        service_definition.add_library(ln)

    # Store a tuple to keep the parser
    service_definitions[service_syntax] = (service_definition, tree)


def parse_service_definitions(xsd_directory, serv_def_files, service_definitions, libraries):
    for serv_def_filename in serv_def_files:
        service_syntax_name = os.path.basename(serv_def_filename).split('.')[0]
        parse_service_definition(xsd_directory, serv_def_filename, service_definitions, service_syntax_name, libraries)

    for n, s in service_definitions.items():
        debug("Service Name: %s %d %d %d" % \
              (n, s[0].get_id(), len(s[0].libraries), len(s[0].operations)))

    return check_service_definitions(service_definitions, libraries)

def __check_serv_dnf_data_type(libraries, serv_dnf, dtype):
    lib_name, data_name = dtype.split(":")
    retval = True

    if lib_name not in serv_dnf.libraries+["ECOA"]:
        retval = False
        error("In service definition %s, library %s doesn't exist" % (serv_dnf.name, lib_name))
    else:
        lib,_ = libraries[lib_name]
        if not lib.is_datatype_defined(data_name):
            retval = False
            error("In service definition %s,in library %s, type %s doesn't exist" % (serv_dnf.name, lib_name, data_name))

    return retval


def check_service_definitions(service_definitions, libraries):
    retval = True

    for serv_dnf,_ in service_definitions.values():
        # check if libraries exist
        for lib_name in serv_dnf.libraries:
            if lib_name not in libraries:
                retval = False
                error("In service definition %s, library %s doesn't exist" % (serv_dnf.name, lib_name))
                continue

        # check if parameters in operations are defined
        for op in serv_dnf.operations:
            if op.nature == 'DATA':
                # check data type
                retval = __check_serv_dnf_data_type(libraries, serv_dnf, op.params[0].type)

            for param in op.params:
                retval = __check_serv_dnf_data_type(libraries, serv_dnf, param.type)

    return  retval
