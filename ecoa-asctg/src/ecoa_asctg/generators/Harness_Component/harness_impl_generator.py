# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

from xml.etree import ElementTree
from ecoa.utilities.namespaces import ECOS_CI
from collections import OrderedDict

from .harness_utils import get_module_type_name, get_module_inst_name,\
    get_module_impl_name, get_trigger_name, get_service_or_reference

def __harness_generate_link_edge(root, edge_str, instance_name, op_name, activating_property=False):
    node = ElementTree.SubElement(root, edge_str)
    if activating_property:
        # link are not activating
        node.set("activating", "false")
    node.set("instanceName", instance_name)
    node.set("operationName", op_name)


def __harness_generate_parameters(root, operation):
    for param in operation.params:
        param_node_name=""
        if param in operation.inputs:
            param_node_name = "input"
        if param in operation.outputs:
            param_node_name = "output"

        ElementTree.SubElement(root, param_node_name, attrib={"name":param.name, "type":param.type})


def __harness_generate_VD(srv_root, op_root, required_service, service_name, label, mod_name, operation):
    new_link_elt = ElementTree.SubElement(srv_root, "dataLink")
    writer_elt = ElementTree.SubElement(new_link_elt, "writers")
    reader_elt = ElementTree.SubElement(new_link_elt, "readers")
    harness_op_name = service_name+"__"+operation.name

    if required_service:
        __harness_generate_link_edge(reader_elt,"moduleInstance", mod_name, harness_op_name, True)
        __harness_generate_link_edge(writer_elt, label, service_name, operation.name)
        new_op_elt = ElementTree.SubElement(op_root, "dataRead", attrib={"name":harness_op_name,
                                                                         "notifying":"false"})
    else:
        __harness_generate_link_edge(reader_elt, label, service_name, operation.name)
        __harness_generate_link_edge(writer_elt,"moduleInstance", mod_name, harness_op_name)
        new_op_elt = ElementTree.SubElement(op_root, "dataWritten", attrib={"name":harness_op_name})

    # generate parameters
    new_op_elt.set("type", operation.params[0].type)


def __harness_generate_event(srv_root, op_root, required_service, service_name, label, mod_name, operation):
    """ Generate an event link and an evenet operation in module type
    """

    new_link_elt = ElementTree.SubElement(srv_root, "eventLink")
    sender_elt = ElementTree.SubElement(new_link_elt, "senders")
    receiver_elt = ElementTree.SubElement(new_link_elt, "receivers")
    harness_op_name = service_name+"__"+operation.name

    if required_service:
        __harness_generate_link_edge(sender_elt,"moduleInstance", mod_name, harness_op_name)
        __harness_generate_link_edge(receiver_elt, label, service_name, operation.name)
        new_op_elt = ElementTree.SubElement(op_root, "eventSent", attrib={"name":harness_op_name})
    else:
        __harness_generate_link_edge(sender_elt, label, service_name, operation.name)
        __harness_generate_link_edge(receiver_elt,"moduleInstance", mod_name, harness_op_name, True)
        new_op_elt = ElementTree.SubElement(op_root, "eventReceived", attrib={"name":harness_op_name})

    # generate parameters
    __harness_generate_parameters(new_op_elt, operation)


def __harness_generate_trigger_event(srv_root, op_root, mod_name, trigger_name):
    # create link
    new_link_elt = ElementTree.SubElement(srv_root, "eventLink")
    sender_elt = ElementTree.SubElement(new_link_elt, "senders")
    receiver_elt = ElementTree.SubElement(new_link_elt, "receivers")

    ElementTree.SubElement(sender_elt, "trigger", attrib={"instanceName":trigger_name, "period":"0.100"})
    __harness_generate_link_edge(receiver_elt,"moduleInstance", mod_name, "HARNESS_Trigger")


    # create event in module type
    ElementTree.SubElement(op_root, "eventReceived", attrib={"name":"HARNESS_Trigger"})


def __harness_generate_RR(srv_root, op_root, required_service, service_name, label, mod_name, operation):
    """ Generate an event link and an event operation in module type
    """

    new_link_elt = ElementTree.SubElement(srv_root, "requestLink")
    sender_elt = ElementTree.SubElement(new_link_elt, "clients")
    receiver_elt = ElementTree.SubElement(new_link_elt, "server")
    harness_op_name = service_name+"__"+operation.name

    if required_service:
        __harness_generate_link_edge(sender_elt,"moduleInstance", mod_name, harness_op_name)
        __harness_generate_link_edge(receiver_elt, label, service_name, operation.name)
        new_op_elt = ElementTree.SubElement(op_root, "requestSent", attrib={"name":harness_op_name})
        new_op_elt.set("timeout","-1")
        new_op_elt.set("isSynchronous","true")
    else:
        __harness_generate_link_edge(sender_elt, label, service_name, operation.name)
        __harness_generate_link_edge(receiver_elt,"moduleInstance", mod_name, harness_op_name, True)
        new_op_elt = ElementTree.SubElement(op_root, "requestReceived", attrib={"name":harness_op_name})

    #generate parameters
    __harness_generate_parameters(new_op_elt, operation)


def harness_generate_comp_impl(libraries, mod_wires_svc, services, references):
    ElementTree.register_namespace("", ECOS_CI[1:-1])
    root = ElementTree.Element(ECOS_CI+"componentImplementation", attrib={"componentDefinition":"HARNESS"})

    # libraries
    for libname in libraries.keys():
        if libname != 'ECOA':
            ElementTree.SubElement(root, "use", attrib={"library":libname})

    # module elements
    mod_type_op_node = OrderedDict() # module_name => xml node
    new_mod_type_name = get_module_type_name()
    mod_inst_name = get_module_inst_name()
    new_mod_impl_name = get_module_impl_name()
    new_trigger_name = get_trigger_name()

    # module type
    mod_type_elt = ElementTree.SubElement(root, "moduleType",
                                          attrib={"name":new_mod_type_name})
    mod_type_op_node_root = ElementTree.SubElement(mod_type_elt,'operations')

    for c_mod_name in mod_wires_svc.keys():
        mod_type_op_node[c_mod_name] = mod_type_op_node_root

    # module implementation
    mod_impl_elt = ElementTree.SubElement(root, "moduleImplementation")
    mod_impl_elt.set("language", "C" )
    mod_impl_elt.set("moduleType", new_mod_type_name)
    mod_impl_elt.set("name", new_mod_impl_name)

    # module instance
    mod_inst_elt = ElementTree.SubElement(root, "moduleInstance")
    mod_inst_elt.set("implementationName", new_mod_impl_name)
    mod_inst_elt.set("name", mod_inst_name)
    mod_inst_elt.set("relativePriority", "100")

    # module trigger
    ElementTree.SubElement(root, "triggerInstance",
                           attrib={"name":new_trigger_name, "relativePriority":"100"})
    __harness_generate_trigger_event(root,
                                     mod_type_op_node_root,
                                     mod_inst_name,
                                     new_trigger_name)


    # generate operations and links for each modules
    for mod_name, op_node in mod_type_op_node.items():
        for syntax, wire in mod_wires_svc.setdefault(mod_name, []):
            if wire.target_component == mod_name:
                is_required_service = True
                service_name = wire.source_service
            else:
                is_required_service = False
                service_name = wire.target_service
            l_label = get_service_or_reference(services, references, service_name)

            for op in syntax.operations:
                if op.nature == 'CMD':
                    __harness_generate_event(root, op_node, is_required_service, service_name, l_label, mod_inst_name, op)
                elif op.nature == 'NOTIFY':
                    # other direction:
                    __harness_generate_event(root, op_node, not is_required_service, service_name, l_label, mod_inst_name, op)
                elif op.nature == 'RR':
                    __harness_generate_RR(root, op_node, is_required_service, service_name, l_label, mod_inst_name, op)
                elif op.nature == 'DATA':
                    __harness_generate_VD(root, op_node, is_required_service, service_name, l_label, mod_inst_name, op)

    return root
