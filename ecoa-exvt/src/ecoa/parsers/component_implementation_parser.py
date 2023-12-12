# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

""" component_implementation_parser module
    to a comp.impl.xml
"""

import os
from xml.etree.ElementTree import ElementTree
from ..models.component_implementation import Component_Implementation
from ..models.operation_type import Parameter
from ..utilities.namespaces import ECOS_CI, ECOS_MB
from ..utilities.logs import debug, error, info, warning
from ..utilities.xml_utils import validate_XML_file
from .component_implementation_checker import check_component_implementation

def is_complex_type(libraries, type_name):
    """ Check if a parameter is complex or not
    """

    for library, _ in libraries.values():
        start = type_name.find(':')
        if library.is_datatype_defined(type_name[start + 1:]):
            return library.get_data_type(type_name[start + 1:]).is_complex_type

    return False

def parse_component_implementations(xsd_directory, comp_impl_files,
                                    component_implementations, libraries):
    for comp_impl_filename in sorted(comp_impl_files):
        parse_comp_impl(xsd_directory, comp_impl_filename, component_implementations, libraries)

def parse_comp_impl(xsd_directory, comp_filename, component_implementations, libraries):
        if not os.path.exists(comp_filename):
            error("component implementation file '%s' does not exist" % (comp_filename))
            return

        comp_impl_name = os.path.basename(comp_filename).replace('.impl.xml', '')
        if comp_impl_name in component_implementations:
            info("component implementation '%s' is already parsed" % (comp_impl_name))
            return

        if validate_XML_file(comp_filename, xsd_directory + "/Schemas_ecoa/ecoa-implementation-2.0.xsd") == -1:
            return

        tree = ElementTree()
        tree.parse(comp_filename)

        component_implementation = Component_Implementation(comp_impl_name, os.path.realpath(os.path.dirname(comp_filename)))
        # componentDefinition = tree.getroot().get("componentDefinition")
        # if componentDefinition != comp_inst.component_type:
        #     warning("componentDefinition "+componentDefinition+" doesn't match with component instance "+ cinstance+" (type: "+comp_inst.component_type+")")

        for lib_node in tree.iterfind(ECOS_CI + "use"):
            name = lib_node.get("library")
            if name != "ECOS" and name != "ECOA":
                component_implementation.add_library(name)

        for mt_node in tree.iterfind(ECOS_CI + "moduleType"):
            name = mt_node.get("name")

            user_context_flag = True if mt_node.get("hasUserContext",
                                        default="true") == "true" else False

            warm_start_context_flag = True if mt_node.get("hasWarmStartContext",
                                        default="true") == "true" else False

            flag = mt_node.get("isFaultHandler")
            fault_handler_flag = (flag == "true")

            component_implementation.add_module_type(name,
                                                     fault_handler_flag, user_context_flag,
                                                     warm_start_context_flag)

            for property_node in mt_node.iterfind(ECOS_CI + "properties"):
                for prop in property_node.iterfind(ECOS_CI + "property"):
                    prop_name = prop.get("name")
                    prop_type = prop.get("type")
                    component_implementation.add_module_type_property(name, prop_name, prop_type,
                                                                      libraries)

            for pinfo_node in mt_node.iterfind(ECOS_CI + "pinfo"):
                for public_pinfo in pinfo_node.iterfind(ECOS_CI+"publicPinfo"):
                    pub_pinfo_name = public_pinfo.get("name")
                    component_implementation.add_module_type_pinfo(name, pub_pinfo_name, False)
                for private_pinfo in pinfo_node.iterfind(ECOS_CI+"privatePinfo"):
                    pri_pinfo_name = private_pinfo.get("name")
                    component_implementation.add_module_type_pinfo(name, pri_pinfo_name, True)

            for ops_node in mt_node.iterfind(ECOS_CI + "operations"):
                for op_node in ops_node.iterfind(ECOS_CI + "eventSent"):
                    op_name = op_node.get("name")
                    params = []
                    for param_node in op_node.iterfind(ECOS_CI + "input"):
                        p_name = param_node.get("name")
                        p_type = param_node.get("type")
                        params.append(Parameter(p_name, p_type, "input"))
                        params[-1].fill_type_property(libraries)
                    component_implementation.add_module_type_operation(name, op_name, "ES", params)
                for op_node in ops_node.iterfind(ECOS_CI + "eventReceived"):
                    op_name = op_node.get("name")
                    params = []
                    for param_node in op_node.iterfind(ECOS_CI + "input"):
                        p_name = param_node.get("name")
                        p_type = param_node.get("type")
                        params.append(Parameter(p_name, p_type, "input"))
                        params[-1].fill_type_property(libraries)
                    component_implementation.add_module_type_operation(name, op_name, "ER", params)
                for op_node in ops_node.iterfind(ECOS_CI + "requestSent"):
                    op_name = op_node.get("name")
                    op_type = op_node.get("isSynchronous")
                    op_max_number = int(op_node.get("maxConcurrentRequests", default="10"))
                    timeout = float(op_node.get("timeout", default="-1"))
                    params = []
                    for param_node in op_node.iterfind(ECOS_CI + "input"):
                        p_name = param_node.get("name")
                        p_type = param_node.get("type")
                        params.append(Parameter(p_name, p_type, "input"))
                        params[-1].fill_type_property(libraries)
                    for param_node in op_node.iterfind(ECOS_CI + "output"):
                        p_name = param_node.get("name")
                        p_type = param_node.get("type")
                        params.append(Parameter(p_name, p_type, "output"))
                        params[-1].fill_type_property(libraries)
                    if op_type == 'true':
                        component_implementation.add_module_type_operation(name, op_name,
                                                                           "SRS", params,
                                                                           timeout=timeout,
                                                                           maxVersions=
                                                                           op_max_number)
                    else:
                        component_implementation.add_module_type_operation(name, op_name,
                                                                           "ARS", params,
                                                                           timeout=timeout,
                                                                           maxVersions=
                                                                           op_max_number)
                for op_node in ops_node.iterfind(ECOS_CI + "requestReceived"):
                    op_name = op_node.get("name")
                    op_max_number = int(op_node.get("maxConcurrentRequests", default="10"))
                    params = []
                    for param_node in op_node.iterfind(ECOS_CI + "input"):
                        p_name = param_node.get("name")
                        p_type = param_node.get("type")
                        params.append(Parameter(p_name, p_type, "input"))
                        params[-1].fill_type_property(libraries)
                    for param_node in op_node.iterfind(ECOS_CI + "output"):
                        p_name = param_node.get("name")
                        p_type = param_node.get("type")
                        params.append(Parameter(p_name, p_type, "output"))
                        params[-1].fill_type_property(libraries)
                    component_implementation.add_module_type_operation(name, op_name,
                                                                       "RR", params,
                                                                       maxVersions=op_max_number)
                for op_node in ops_node.iterfind(ECOS_CI + "dataWritten"):
                    op_name = op_node.get("name")
                    op_type = op_node.get("type")
                    maxVersion = op_node.get("maxVersions")
                    writeOnly = False if op_node.get("writeOnly", default="false") == "false" else True
                    if maxVersion is None:
                        maxVersion = 1
                    else:
                        maxVersion = int(maxVersion)
                    params = []
                    params.append(Parameter(op_name, op_type, "input"))
                    params[-1].fill_type_property(libraries)
                    component_implementation.add_module_type_operation(name, op_name,
                                                                       "DW", params,
                                                                       maxVersions=maxVersion,
                                                                       writeOnly=writeOnly)
                for op_node in ops_node.iterfind(ECOS_CI + "dataRead"):
                    op_name = op_node.get("name")
                    op_type = op_node.get("type")
                    op_notifying = op_node.get("notifying")
                    maxVersion = int(op_node.get("maxVersions", default=1))

                    params = []
                    params.append(Parameter(op_name, op_type, "input"))
                    params[-1].fill_type_property(libraries)
                    if op_notifying == "true":
                        component_implementation.add_module_type_operation(name, op_name,
                                                                           "DRN", params,
                                                                           maxVersions=maxVersion)
                    else:
                        component_implementation.add_module_type_operation(name, op_name,
                                                                           "DR", params,
                                                                           maxVersions=maxVersion)

        for mim_node in tree.iterfind(ECOS_CI + "moduleImplementation"):
            name = mim_node.get("name")
            mtype = mim_node.get("moduleType")
            mlanguage = mim_node.get("language")
            component_implementation.add_module_implementation(name,
                                                               mtype,
                                                               mlanguage)

        module_index = 0
        for mi_node in tree.iterfind(ECOS_CI + "moduleInstance"):
            name = mi_node.get("name")
            miname = mi_node.get("implementationName")
            mi_relative_priority = mi_node.get("relativePriority")
            mbehaviour = mi_node.get("moduleBehaviour")
            if mbehaviour:
                behaviour_filename = os.path.dirname(comp_filename) + '/' + \
                                     mbehaviour.replace(".behaviour.xml", "") + ".behaviour.xml"
                (wcet, deadline) = parse_module_behaviour(behaviour_filename)
            else:
                mbehaviour = name + ".behaviour.xml"
                (wcet, deadline) = (0, 0)

            debug('WCET for ' + mbehaviour + " : " + str(wcet))
            component_implementation.add_module_instance(name,
                                                         module_index,
                                                         miname,
                                                         mbehaviour,
                                                         mi_relative_priority,
                                                         deadline,
                                                         wcet)
            module_index += 1
            mod_inst = component_implementation.get_instance(name)
            mod_type = component_implementation.find_module_type(name)
            for prop_val_node in mi_node.iterfind(ECOS_CI + "propertyValues"):
                for prop_val in prop_val_node.iterfind(ECOS_CI + "propertyValue"):
                    p_name = prop_val.get("name")
                    # remove whitespace at the begining and at the end
                    p_val = prop_val.text.lstrip().rstrip() if prop_val.text else None
                    mod_inst.add_property_value(mod_type, p_name, p_val)

            for pinfo_node in mi_node.iterfind(ECOS_CI + "pinfo"):
                for public_pinfo in pinfo_node.iterfind(ECOS_CI+"publicPinfo"):
                    pub_pinfo_name = public_pinfo.get("name")
                    pub_pinfo_val = public_pinfo.text.lstrip().rstrip() if public_pinfo.text else None
                    component_implementation.add_module_inst_pinfo_value(name,
                                                                         mod_type,
                                                                         pub_pinfo_name,
                                                                         pub_pinfo_val,
                                                                         False)
                for private_pinfo in pinfo_node.iterfind(ECOS_CI+"privatePinfo"):
                    pri_pinfo_name = private_pinfo.get("name")
                    pri_pinfo_val = private_pinfo.text.lstrip().rstrip() if private_pinfo.text else None
                    component_implementation.add_module_inst_pinfo_value(name, mod_type,
                                                                         pri_pinfo_name,
                                                                         pri_pinfo_val, True)


        trigger_index = 0
        for ti_node in tree.iterfind(ECOS_CI + "triggerInstance"):
            name = ti_node.get("name")
            mbehaviour = ti_node.get("moduleBehaviour")
            if mbehaviour:
                behaviour_filename = os.path.dirname(comp_filename) + '/' + \
                                     mbehaviour.replace(".behaviour.xml", "") + ".behaviour.xml"
                (wcet, deadline) = parse_module_behaviour(behaviour_filename)
            else:
                mbehaviour = name + ".behaviour.xml"
                (wcet, deadline) = 0, 0

            debug('WCET for ' + mbehaviour + " : " + str(wcet))
            component_implementation.add_trigger_instance(name, trigger_index,
                                                          mbehaviour,
                                                          deadline,
                                                          wcet)
            trigger_index += 1

        dynamic_trigger_index = 0
        for dti_node in tree.iterfind(ECOS_CI + "dynamicTriggerInstance"):
            name = dti_node.get("name")
            mbehaviour = dti_node.get("moduleBehaviour")
            if mbehaviour:
                behaviour_filename = os.path.dirname(comp_filename) + '/' + \
                                     mbehaviour.replace(".behaviour.xml", "") + ".behaviour.xml"
                (wcet, deadline) = parse_module_behaviour(behaviour_filename)
            else:
                mbehaviour = name + ".behaviour.xml"
                (wcet, deadline) = (0, 0)
            debug('WCET for ' + mbehaviour + " : " + str(wcet))
            size = dti_node.get("size")
            if size is not None:
                size = int(size)
            else:
                size = 1

            component_implementation.add_dynamic_trigger_instance(name, dynamic_trigger_index,
                                                                  mbehaviour,
                                                                  deadline,
                                                                  wcet,
                                                                  size)
            params = []
            for param in dti_node.iterfind(ECOS_CI + "parameter"):
                p_name = param.get("name")
                p_type = param.get("type")
                params.append(Parameter(p_name, p_type, "input"))
                params[-1].fill_type_property(libraries)
            component_implementation.dynamic_trigger_instances[
                dynamic_trigger_index].set_params(params)

            dynamic_trigger_index += 1

        for opl in tree.iterfind(ECOS_CI + "dataLink"):
            accessControl = False if opl.get("controlled", default="true") == "false" else True
            new_vd = component_implementation.add_vd_repository(accessControl)

            writers_list = []
            for writers in opl.iterfind(ECOS_CI + "writers"):
                for module_inst in writers.iterfind(ECOS_CI + "moduleInstance"):
                    name = module_inst.get("instanceName")
                    op_name = module_inst.get("operationName")
                    writers_list.append((name, op_name))
                    new_vd.add_writer(name, op_name)
                for service_inst in writers.iterfind(ECOS_CI + "service"):
                    assert 0
                for reference_inst in writers.iterfind(ECOS_CI + "reference"):
                    name = reference_inst.get("instanceName")
                    op_name = reference_inst.get("operationName")
                    writers_list.append((name, op_name))
                    new_vd.add_writer(name, op_name)

            readers_list = []
            for readers in opl.iterfind(ECOS_CI + "readers"):
                for module_inst in readers.iterfind(ECOS_CI + "moduleInstance"):
                    name = module_inst.get("instanceName")
                    op_name = module_inst.get("operationName")
                    fifo_size = int(module_inst.get("fifoSize", default="8"))
                    activating_op = True if module_inst.get("activating",
                                                            default="true") == "true" else False
                    new_vd.add_reader_module(name, op_name, fifo_size, activating_op)

                    readers_list.append((name, op_name, fifo_size, activating_op))
                for service_inst in readers.iterfind(ECOS_CI + "service"):
                    name = service_inst.get("instanceName")
                    op_name = service_inst.get("operationName")
                    new_vd.add_reader_service(name, op_name)
                    readers_list.append((name, op_name))
                for reference_inst in readers.iterfind(ECOS_CI + "reference"):
                    assert 0


            for writer in writers_list:
                for reader in readers_list:
                    mod_link = component_implementation.add_module_link(writer[0], writer[1], "reference",
                                                                        reader[0], reader[1], "service",
                                                                        "data")
                    if len(reader) > 3:
                        mod_link.set_fifoSize(reader[2])
                        mod_link.activating_op = reader[3]
                if len(readers_list) == 0:
                    mod_link2 = component_implementation.add_module_link(writer[0], writer[1], "reference",
                                                                         "", "", "service",
                                                                         "data")

        # Parse eventLinks
        for opl in tree.iterfind(ECOS_CI + "eventLink"):
            senders_list = []
            for senders in opl.iterfind(ECOS_CI + "senders"):
                for module_inst in senders.iterfind(ECOS_CI + "moduleInstance"):
                    name = module_inst.get("instanceName")
                    op_name = module_inst.get("operationName")
                    senders_list.append((name, op_name, "moduleInstance"))
                for trigger_inst in senders.iterfind(ECOS_CI + "trigger"):
                    name = trigger_inst.get("instanceName")
                    op_name = trigger_inst.get("period")
                    senders_list.append((name, op_name, "trigger"))
                for dtrigger_inst in senders.iterfind(ECOS_CI + "dynamicTrigger"):
                    name = dtrigger_inst.get("instanceName")
                    op_name = dtrigger_inst.get("operationName")
                    senders_list.append((name, op_name, "dynamicTrigger"))
                for service_inst in senders.iterfind(ECOS_CI + "service"):
                    name = service_inst.get("instanceName")
                    op_name = service_inst.get("operationName")
                    senders_list.append((name, op_name, "service"))
                for reference_inst in senders.iterfind(ECOS_CI + "reference"):
                    name = reference_inst.get("instanceName")
                    op_name = reference_inst.get("operationName")
                    senders_list.append((name, op_name, "reference"))
                for reference_inst in senders.iterfind(ECOS_CI + "external"):
                    name = None
                    op_name = reference_inst.get("operationName")
                    mlanguage = reference_inst.get("language")
                    senders_list.append((name, op_name, "external_"+mlanguage))
            receivers_list = []
            for receivers in opl.iterfind(ECOS_CI + "receivers"):
                for module_inst in receivers.iterfind(ECOS_CI + "moduleInstance"):
                    name = module_inst.get("instanceName")
                    op_name = module_inst.get("operationName")
                    fifo_size = int(module_inst.get("fifoSize", default="8"))
                    activating_op = True if module_inst.get("activating",
                                                            default="true") == "true" else False
                    receivers_list.append((name, op_name, "moduleInstance", fifo_size, activating_op))
                for dtrigger_inst in receivers.iterfind(ECOS_CI + "dynamicTrigger"):
                    name = dtrigger_inst.get("instanceName")
                    op_name = dtrigger_inst.get("operationName")
                    fifo_size = int(dtrigger_inst.get("fifoSize", default="8"))
                    receivers_list.append((name, op_name, "dynamicTrigger", fifo_size))
                for service_inst in receivers.iterfind(ECOS_CI + "service"):
                    name = service_inst.get("instanceName")
                    op_name = service_inst.get("operationName")
                    receivers_list.append((name, op_name, "service"))
                for reference_inst in receivers.iterfind(ECOS_CI + "reference"):
                    name = reference_inst.get("instanceName")
                    op_name = reference_inst.get("operationName")
                    receivers_list.append((name, op_name, "reference"))
            for sender in senders_list:
                for receiver in receivers_list:
                    mod_link = component_implementation.add_module_link(sender[0], sender[1], sender[2],
                                                                        receiver[0], receiver[1], receiver[2],
                                                                        "event")
                    if len(receiver) > 3:
                        mod_link.set_fifoSize(receiver[3])
                    if len(receiver) > 4:
                        mod_link.activating_op = receiver[4]

        # Parse requestLinks
        for opl in tree.iterfind(ECOS_CI + "requestLink"):
            clients_list = []
            for clients in opl.iterfind(ECOS_CI + "clients"):
                for module_inst in clients.iterfind(ECOS_CI + "moduleInstance"):
                    activating_op = True if module_inst.get("activating",
                                                            default="true") == "true" else False
                    name = module_inst.get("instanceName")
                    op_name = module_inst.get("operationName")
                    clients_list.append((name, op_name, "moduleInstance", activating_op))
                for service_inst in clients.iterfind(ECOS_CI + "service"):
                    name = service_inst.get("instanceName")
                    op_name = service_inst.get("operationName")
                    clients_list.append((name, op_name, "service"))
                for reference_inst in clients.iterfind(ECOS_CI + "reference"):
                    name = reference_inst.get("instanceName")
                    op_name = reference_inst.get("operationName")
                    clients_list.append((name, op_name, "reference"))
            server_list = []
            for server in opl.iterfind(ECOS_CI + "server"):
                for module_inst in server.iterfind(ECOS_CI + "moduleInstance"):
                    name = module_inst.get("instanceName")
                    op_name = module_inst.get("operationName")
                    fifo_size = int(module_inst.get("fifoSize", default="8"))
                    activating_op = True if module_inst.get("activating",
                                                            default="true") == "true" else False
                    server_list.append((name, op_name, "moduleInstance", fifo_size, activating_op))
                for service_inst in server.iterfind(ECOS_CI + "service"):
                    name = service_inst.get("instanceName")
                    op_name = service_inst.get("operationName")
                    server_list.append((name, op_name, "service"))
                for reference_inst in server.iterfind(ECOS_CI + "reference"):
                    name = reference_inst.get("instanceName")
                    op_name = reference_inst.get("operationName")
                    server_list.append((name, op_name, "reference"))
            if len(server_list) != 1:
                warning("No single server for RR operation %s" % (op_name))
            for client in clients_list:
                for server in server_list:
                    mod_link = component_implementation.add_module_link(client[0], client[1], client[2],
                                                                        server[0], server[1], server[2],
                                                                        "RR")
                    if len(server) > 3:
                        mod_link.set_fifoSize(server[3])
                        mod_link.activating_op = server[4]
                    else:
                        mod_link.set_fifoSize(8)

                    if len(client) > 3:
                        # TODO: activating operation for client only
                        mod_link.activating_RR_answer = client[3]

        # Store a tuple to keep the parser
        component_implementations[comp_impl_name] = (component_implementation, tree)



def parse_module_behaviour(filename):
    """ Return the tuple wcet, deadline
    """

    wcet = 0

    if not os.path.exists(filename):
        error("Following module behaviour file does not exist: %s" % (filename))
        return (-1, -1)

    tree = ElementTree()
    tree.parse(filename)

    #    for e in tree.iter():
    #        print e.tag

    for entry_node in tree.iterfind(ECOS_MB + "entryPoint"):
        ewcet = 0
        for action_node in entry_node.iterfind(ECOS_MB + "action"):
            maxcomputingsteps = 0
            for computing_node in action_node.iterfind(ECOS_MB + "computing"):
                maxcomputingsteps = maxcomputingsteps + int(computing_node.get("maxComputingSteps"))
            ewcet = ewcet + maxcomputingsteps

        if ewcet > wcet:
            wcet = ewcet

    return (wcet, 0)


## Check if component implementation is consistent to the previously defined module, trigger,
# service_definitions and operations defined
def check_all_component_implementations(components, component_implementations, component_types,
                                    service_definitions, libraries, composite):
    """ Check the consistency of component implementation definitions
    """

    success = True
    # TODO for loop with component implementation instead of component instance
    for comp_instance in components.values():
        cimpl_name = components[comp_instance.name].get_component_implementation()
        if comp_instance.get_component_type() not in component_types:
            warning("Type of component '" + comp_instance.name + "' is undefined : '" + comp_instance.get_component_type() + "'")
            continue
        component_type = component_types[comp_instance.get_component_type()][0]

        if component_type is None:
            error("Unknown component type " +comp_instance.get_component_type())
            success = False
            continue

        if cimpl_name == "":
            # component without component implementation (define in an other Plaform)
            pass
        elif cimpl_name not in component_implementations:
            error("Unknown component implementation " +cimpl_name)
            success = False
            continue
        else:
            # check component implementation
            component_impl = component_implementations[cimpl_name][0]
            if not check_component_implementation(comp_instance, component_impl, component_type,
                                        service_definitions, libraries, composite, component_implementations):
                success = False


    return success
