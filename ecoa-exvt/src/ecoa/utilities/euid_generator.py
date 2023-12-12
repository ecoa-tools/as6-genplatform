# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

import os
import logging
from ..utilities.logs import debug, error, info, warning
import hashlib
from collections import OrderedDict

def _generate_ID_value(ID_str):
    hash_val = hashlib.md5(ID_str.encode('utf-8')).hexdigest()
    # return a 32 bits integer greater than 100
    return (int(hash_val, 16)+100) % ((1<<31) -1)

def find_IDs(IDs, wires, components, component_types, service_definitions):
    """Find missing ID operations of wires

    Attributes:
        IDs                 (dict): existing IDs
        wires               (dict): dictionary of Wire.
                                Operations that handle these wires must have an ID
        components          (dict): dictionary of components
        component_types     (dict): dictionary of component types
        service_definitions (dict): dictionary of service definitions

    Return:
        (dict) : dictionary of new IDs
    """
    id_already_used = IDs.values()
    new_IDs=OrderedDict()
    for w in wires:
        syntax = w.find_service_syntax(components, component_types, service_definitions)
        for op in syntax.operations:
            key = w.source_component+"/"+\
                  w.source_service + ":"+\
                  w.target_component+"/"+\
                  w.target_service + ":"+\
                  op.name
            if key not in IDs and key not in new_IDs:
                value = _generate_ID_value(key)
                new_IDs[key] = str(value)

    return new_IDs

def generate_EUID_keys(ID_keys):
    EUIDs_dict=OrderedDict()
    for key in ID_keys:
        EUIDs_dict[key]= str(_generate_ID_value(key))
    return EUIDs_dict

def generate_IDs(new_IDs, filename):
    """Generate new XML file with new IDs

    Attributes:
        new_IDs  (dict): dictionary of new IDs
        filename (str) : file name to generate

    """

    ID_tmpl="<ID key=\"#KEY#\" value=\"#VALUE#\"/>\n"
    generated_ids_str=""
    for key, value in new_IDs.items():
        generated_ids_str+="  "+ID_tmpl.replace("#KEY#", key)\
                                       .replace("#VALUE#", value)

    string =""
    if generated_ids_str != "":
        info("generated file '%s'" % (filename))
        string += "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>\n"+\
                  "<ID_map xmlns=\"http://www.ecoa.technology/uid-2.0\">\n"

        string += generated_ids_str
        string += "</ID_map>\n"
    else:
        debug("No EUIDs to generate in file '%s'" % (filename))
        return

    if os.path.exists(filename):
        logging.disable(level=logging.NOTSET)
        warning("file '%s' already exist. Cannot create new EUIDs file." % (filename) +\
                "This file may be need to be added in xxx.project.xml?")
        logging.disable(level=logging.CRITICAL)
        info("add these lines in file '"+filename+"' :\n\n"+generated_ids_str+"\n")
    else:
        file = open(filename, 'w')
        print(string, file=file)
        file.close()


def check_IDs_unicity(IDs_dict):
    set_of_values = set()
    for key, value in IDs_dict.items():
        if value in set_of_values:
            error("ID collision: key = '%s', value = '%s'"%(key,value))
        else:
            set_of_values.add(value)

        if int(value) < 100:
            warning("ID '%s' : value is lower than 100. Theses values are reserved for platform operations" %(key))

def check_cross_PF_IDs_consistency(wire, wire_syntax, current_PF_name, other_pf_name, current_pf_composite_type,
                                    components,  cross_PF_view, PF_IDs):
    """Checks consistency between cross PF IDs and local platform ID. finds missing local IDs that should have the same value of a cross PF IDs

    Attributes:
        wire                           (:class:`..Wire`):The wire to check (connected with on other platform)
        wire_syntax      (:class:`..Service_Definition`):The wire syntax
        current_PF_name                            (str):The current PF name
        other_pf_name                              (str):The other PF name
        current_pf_composite_type (:class:`..Composite`):The current PF composite type
        components                                (dict):The local platform components
        cross_PF_view  (:class:`..cross_platforms_view`):The cross PF view
        PF_IDs                                    (dict):The local platform IDs

    Return:
        dictionary of missing local IDs that should have the same value of a cross PF IDs
    """
    new_PF_IDs = OrderedDict()

    # find other PF composite
    other_pf_composite = cross_PF_view.find_composite_name(other_pf_name)

    # find current PF composite
    current_pf_composite = cross_PF_view.find_composite_name(current_PF_name)

    # find ID key base (cross PF view)
    cross_pf_wire_key_base=""
    cross_pf_wire = []

    if components[wire.source_component].component_implementation == "":
        other_pf_service = current_pf_composite_type.find_promoted_service(wire.target_component, wire.target_service)
        cross_pf_wire_key_base=other_pf_composite+"/"+wire.source_service+":"+current_pf_composite+"/"+other_pf_service

        ##################### hack to support invalid case
        list_services = current_pf_composite_type.find_promoted_services(wire.target_component, wire.target_service)
        for serv_name in list_services:
            for w in cross_PF_view.cross_PF_wire_mapping[wire.PF_link_id]:
                if w.source_component == other_pf_composite and w.source_service == wire.source_service and\
                    w.target_component == current_pf_composite and w.target_service == serv_name:
                    cross_pf_wire_key_base = other_pf_composite+"/"+wire.source_service+":"+current_pf_composite+"/"+serv_name
        ###################################

    else:
        other_pf_reference = current_pf_composite_type.find_promoted_reference(wire.source_component, wire.source_service)
        cross_pf_wire_key_base=current_pf_composite+"/"+other_pf_reference+":"+other_pf_composite+"/"+wire.target_service


    # for every operations of this wire:
    for op in wire_syntax.operations:
        local_key = wire.__repr__()+":"+op.name
        cross_pf_key = cross_pf_wire_key_base+":"+op.name
        euid_filename = cross_PF_view.euid_binding[wire.PF_link_id]
        cross_pf_dict = cross_PF_view.EUIDs[euid_filename]

        if cross_pf_key in cross_pf_dict:
            cross_pf_id = cross_pf_dict[cross_pf_key]
            if local_key not in PF_IDs:
                # new local ID with the rigth value
                new_PF_IDs[local_key] = cross_pf_id
            else:
                local_id = PF_IDs[local_key]

                if( cross_pf_id != local_id):
                    error("invalid EUID between: \n   ('%s' = %s)\n   ('%s' = %s)" %
                        (local_key, local_id, cross_pf_key, cross_pf_id))
        else:
            warning("Cannot check id consictency of wire "+local_key+". '"+cross_pf_key+"' doesn't exist in "+euid_filename)

    return new_PF_IDs
