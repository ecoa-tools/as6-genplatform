# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

"""
This file contains function to generate context of normal module, trigger and dynamic trigger
"""
import os, shutil
from .properties_generator import property_init_generate
from ecoa.utilities.logs import debug, error
from ..fix_names import fix_C_data_type

def generate_generic_mod_context(ctx_str, protection_domain, deployed_mod, components):
    text="\n    // context for module "+deployed_mod.name+"\n"
    text+=ctx_str+".name = \""+deployed_mod.name+"\";\n"
    text+=ctx_str+".mod_id = "+str(deployed_mod.id+protection_domain.id_counter)+";\n"
    text+=ctx_str+".network_write_data = malloc(sizeof(net_data_w));\n"
    text+=ctx_str+".network_write_data->module_id = "+str(deployed_mod.id+2)+";\n"
    text+=ctx_str+".network_write_data->msg_id = 100;\n"
    text+=ctx_str+".component_name = \""+deployed_mod.component_name+"\";\n"
    text+=ctx_str+".mem_pool = mem_pool;\n"
    text+=ctx_str+".state = IDLE;\n"
    text+=ctx_str+".msg_buffer_size = "+protection_domain.name+"_compute_buffer_size();\n"
    text+=ctx_str+".msg_buffer = NULL;\n"
    text+=ctx_str+".component_ctx = ctx ;\n"

    text+=ctx_str+".logger_PF = ctx->logger_PF ;\n"
    text+=ctx_str+".priority = "+str(components[deployed_mod.component_name].mod_relocated_priority[deployed_mod.name])+";// ??\n"

    text += generate_cpu_mask(ctx_str, deployed_mod, protection_domain)

    return text

def generate_dyn_trigger_mod_context(ctx_str, protection_domain, deployed_mod, components,
                                     component_implementations,
                                     wires, component_types):
    """@TODO Function docstring"""
    comp = components[deployed_mod.component_name]
    comp_impl = component_implementations[comp.component_implementation][0]
    comp_type, _ = component_types[comp.component_type]
    d_trig_inst = comp_impl.get_instance(deployed_mod.name)
    text = ""

    text += generate_fifo_manager(ctx_str, len(d_trig_inst.entry_links_index), d_trig_inst.fifo_size)
    text += generate_fifo_manager_dyn_trigger(ctx_str, d_trig_inst)

    text += ctx_str + ".max_event_nb = " + str(d_trig_inst.size) + ";\n"

    text += ctx_str + ".operation_num = " + str(len(d_trig_inst.out_points_dict)) + ";\n"
    text += ctx_str + ".operation_map = calloc(" + str(
        len(d_trig_inst.out_points_dict)) + ",sizeof(ldp_mod_operation_map));\n"
    text += ctx_str + ".params_size = 0"
    for param in d_trig_inst.params:
        text += "+sizeof(" + fix_C_data_type(param.type) + ")"
    text += ";\n"
    for out_op_index, (_, link_list) in enumerate(d_trig_inst.out_points_dict.items()):
        string_operation_map = ctx_str + ".operation_map[" + str(out_op_index) + "]"

        text += generate_operation_map(string_operation_map,
                                       link_list,
                                       "d_trigger_event_" + str(out_op_index),
                                       deployed_mod,
                                       protection_domain,
                                       wires,
                                       component_implementations,
                                       components,
                                       comp_type,
                                       None)

    return text


def generate_trigger_mod_context(ctx_str, protection_domain, deployed_mod, components,
                                 component_implementations, wires,
                                 component_types):
    """@TODO Function docstring"""
    comp = components[deployed_mod.component_name]
    comp_impl = component_implementations[comp.component_implementation][0]
    comp_type, _ = component_types[comp.component_type]
    trig_inst = comp_impl.get_instance(deployed_mod.name)
    text = ""

    text += ctx_str + ".logger = NULL;\n"
    text += generate_fifo_manager(ctx_str, len(trig_inst.entry_links_index), trig_inst.fifo_size)

    text += ctx_str + ".nb_trigger_event = " + str(len(trig_inst.out_points_dict)) + ";\n"
    text += ctx_str + ".trigger_events = calloc(" + str(
        len(trig_inst.out_points_dict)) + ",sizeof(ldp_trigger_event_context));\n"

    tmp_str = ""
    op_map_index = 0
    for trigger_period_index, (period, link_list) in enumerate(trig_inst.out_points_dict.items()):
        tmp_str += "   // event for period " + period + "\n"
        tmp_str += ctx_str + ".trigger_events[" + str(
            trigger_period_index) + "].period = " + period + ";\n"
        tmp_str += ctx_str + ".trigger_events[" + str(
            trigger_period_index) + "].nb_operations=" + str(
                len(link_list)) + ";\n"
        tmp_str += ctx_str + ".trigger_events[" + str(
            trigger_period_index) + "].operation_indexes = calloc(" + str(
                len(link_list)) + ", sizeof(int));\n"

        for i, index in enumerate(range(op_map_index, op_map_index + len(link_list))):
            tmp_str += ctx_str + ".trigger_events[" + str(
                trigger_period_index) + "].operation_indexes[" + str(
                    i) + "]=" + str(index) + ";\n"

        for link in link_list:
            string_operation_map = ctx_str + ".operation_map[" + str(op_map_index) + "]"
            tmp_str += generate_operation_map(string_operation_map,
                                              [link],
                                              link.target_operation,
                                              deployed_mod,
                                              protection_domain,
                                              wires,
                                              component_implementations,
                                              components,
                                              comp_type,
                                              None)
            op_map_index += 1

    text += ctx_str + ".operation_num = " + str(op_map_index) + ";\n"
    text += ctx_str + ".operation_map = calloc(" + str(
        op_map_index) + ", sizeof(ldp_mod_operation_map));\n"
    text += tmp_str

    return text


def generate_normal_mod_context(directory, ctx_str, protection_domain, deployed_mod, components,
                                component_implementations, wires,
                                libraries, component_types,
                                group_ID=0, ctx_master_str=None):
    """@TODO Function docstring"""
    comp = components[deployed_mod.component_name]
    comp_impl = component_implementations[comp.component_implementation][0]
    comp_type, _ = component_types[comp.component_type]

    mod_inst = comp_impl.get_instance(deployed_mod.name)
    mod_impl = comp_impl.module_implementations[mod_inst.implementation]
    mod_type = comp_impl.module_types[mod_impl.type]

    text = ""

    text += generate_log_structure(ctx_str, deployed_mod, comp, mod_inst)

    l_nb_internal_pool = 0
    l_nb_internal_pool_num = 0 #Used for the calloc of the pool
    l_fifo_size = 0

    text += generate_fifo_manager(ctx_str, len(mod_inst.entry_links_index)+l_nb_internal_pool, mod_inst.fifo_size+l_fifo_size)
    text += generate_fifo_manager_module(ctx_str, mod_inst, l_fifo_size, mod_type, comp)

    # PINFO
    text += generate_mod_pinfo_ctx(directory, ctx_str, mod_type, mod_inst, comp)

    # Versioned Data
    space=""
    text += generate_mod_VD_manager(ctx_str, space, mod_inst, protection_domain, comp)

    # properties
    text += generate_mod_properties_ctx(ctx_str, mod_type, mod_inst, comp, libraries)

    # operation map
    out_op_number = len(mod_inst.out_points_dict)
    text += "    // output operation map\n"
    text += ctx_str + ".operation_num = " + str(out_op_number) + ";\n"
    text += ctx_str + ".operation_map = calloc(" + str(
        out_op_number) + ", sizeof(ldp_mod_operation_map));\n"
    for op_name in mod_inst.out_points_dict:
        op = mod_type.operations[op_name]
        links_list = mod_inst.out_points_dict[op.name]

        string_operation_map = ctx_str + ".operation_map[" + str(op.op_output_index) + "]"
        text += generate_operation_map(string_operation_map,
                                       links_list,
                                       op.name,
                                       deployed_mod,
                                       protection_domain,
                                       wires,
                                       component_implementations,
                                       components,
                                       comp_type,
                                       op)

    # RR
    # if module contains RR operations
    if mod_type.has_RR_operations():
        num_of_req_sent = sum(
            [op.maxVersions for op in mod_type.operations.values() if op.type in ['ARS', 'SRS']])
        num_of_req_recv = sum(
            [op.maxVersions for op in mod_type.operations.values() if op.type in ['RR']]) + len(
                [op for op in mod_type.operations.values() if op.type in ['ARS', 'SRS']])
        num_of_rr_op = len(
            [op for op in mod_type.operations.values() if op.type in ['ARS', 'SRS', 'RR']])
        text += "\n"
        text += "   ldp_init_request_response(&ctx->worker_context[" + str(
            deployed_mod.index) + "].req_resp," + str(
                num_of_req_recv) \
                    + "," + str(num_of_req_sent) + "," + str(num_of_rr_op) + ", ctx->mem_pool);\n"
    else:
        text += "   ldp_init_request_response(&ctx->worker_context[" + str(
            deployed_mod.index) + "].req_resp, 0, 0,0, ctx->mem_pool);\n"

    return text

def generate_operation_map_add_mod(string_operation_map, sender_mod_inst,
                                   link_mod_index, deployed_receiver_mod, receiver_mod_inst,
                                   receiver_link, sender_link):
    """@TODO Function docstring"""

    mod_receiver_template="\
    // op '#OP_NAME#' of module '#MOD_NAME#' in component '#COMP_NAME#'\n\
#CONTEXT#.module_operations[#LINK_INDEX#].mod_ctx = #MOD_CTX#;\n\
#CONTEXT#.module_operations[#LINK_INDEX#].op_id = #COMP_NAME#__#MOD_NAME#__#OP_NAME#; // #LINK_ID#\n\
#CONTEXT#.module_operations[#LINK_INDEX#].op_index = #OP_INDEX#;\n\
#CONTEXT#.module_operations[#LINK_INDEX#].op_activating = #ACTIVATING#;\n"

    mod_receiver_RR_answer_template="\
#CONTEXT#.module_operations[#LINK_INDEX#].RR_answer_op_index = #RR_OP_INDEX#;     // property of RR answer\n\
#CONTEXT#.module_operations[#LINK_INDEX#].RR_answer_activating = #RR_ACTIVATING#; // property of RR answer\n"

    # receiver module context string
    if deployed_receiver_mod.type == "trigger":
        receiver_mod_ctx_str = "(void*)&ctx->dyn_trigger_context"
    else:
        receiver_mod_ctx_str = "&ctx->worker_context"
    receiver_mod_ctx_str += "[" + str(deployed_receiver_mod.index) + "]"

    # receiver operation name
    if receiver_mod_inst.name == receiver_link.target:
        op_name = receiver_link.target_operation
    else:
        op_name = receiver_link.source_operation


    text = mod_receiver_template.replace("#OP_NAME#", op_name)\
                                .replace("#MOD_NAME#", deployed_receiver_mod.name)\
                                .replace("#COMP_NAME#", deployed_receiver_mod.component_name)\
                                .replace("#MOD_CTX#", receiver_mod_ctx_str)\
                                .replace("#OP_INDEX#", str(receiver_mod_inst.entry_links_index[op_name][0]))\
                                .replace("#LINK_ID#", receiver_link.get_op_id())\
                                .replace("#ACTIVATING#", str(receiver_link.activating_op).lower())

    if receiver_link.type == 'RR' and receiver_link.target == receiver_mod_inst.name:
        # to receive RR answer
        text += mod_receiver_RR_answer_template \
                  .replace("#RR_ACTIVATING#", str(sender_link.activating_RR_answer).lower())\
                  .replace("#RR_OP_INDEX#", str(sender_mod_inst.entry_links_index[sender_link.source_operation][0]))

    text = text.replace("#CONTEXT#", string_operation_map)\
               .replace("#LINK_INDEX#", str(link_mod_index))

    return text


def generate_operation_map(ctx_str, links_list, op_name, deployed_mod, protection_domain, wires,
                           component_implementations, components, comp_type,
                           op):
    """Generate operation map for the operation of a deployed module regarding the list of connected links
    """
    text_op_map = ""
    l_mod_index = 0
    l_sock_index = 0
    l_PF_sock_index = 0


    comp = components[deployed_mod.component_name]
    comp_impl = component_implementations[comp.component_implementation][0]
    sender_mod_inst = comp_impl.get_instance(deployed_mod.name)

    for l in links_list:
        if l.type == "data":
            assert(0)

        if l.target == "":
            # unconnected operation (DW)*
            debug(" unconnected operation: operation_map is not generated for link: "+str(l))
            return ""

        if l.is_between_modules(comp_impl):
            # l between 2 deployed mod in the same comp
            if deployed_mod.name == l.source:
                link_op_name = l.target_operation
                receiver_mod_inst = comp_impl.get_instance(l.target)
            else:
                link_op_name = l.source_operation
                receiver_mod_inst = comp_impl.get_instance(l.source)
            if receiver_mod_inst is None:
                error("connected module not found in componnent " + comp_impl.name + "for link " + str(l))

            deployed_receiver_mod = protection_domain.find_deployed_module(receiver_mod_inst.name, comp.name)
            text_op_map += generate_operation_map_add_mod(ctx_str, sender_mod_inst,
                                                          l_mod_index,
                                                          deployed_receiver_mod, receiver_mod_inst,
                                                          l, l) #sender_link and receiver_link are the same
            l_mod_index += 1
        else:
            # link between a module and a service/reference
            # => communication to a fifo
            connected_wires = l.find_connected_wires_link(comp.name, wires)
            for w in connected_wires:
                # for inside link


                if w in protection_domain.internal_wires_connection:
                    if w.target_component != deployed_mod.component_name:
                        comp2 = components[w.target_component]
                    else:
                        comp2 = components[w.source_component]

                    if comp2.component_implementation == "":
                        #external PF wire: this case is handle below
                        continue

                    comp_impl2 = component_implementations[comp2.component_implementation][0]

                    for l1, l2 in protection_domain.internal_wires_connection[w]:
                        # for all links connected with a wire but that connect 2 modules in the
                        #  same protection domain
                        # => communication to a fifo
                        if l1 == l:
                            receiver_mod_inst = comp_impl2.get_instance(l2.target)
                            receiver_link = l2 # link connected with the current module (and the wire)
                            sender_link = l1  # link connected with the other module (and the wire)
                        elif l2 == l:
                            receiver_mod_inst = comp_impl2.get_instance(l1.source)
                            receiver_link = l1
                            sender_link = l2
                        else:
                            continue


                        deployed_receiver_mod = protection_domain.find_deployed_module(receiver_mod_inst.name,
                                                                                      comp2.name)
                        text_op_map += generate_operation_map_add_mod(ctx_str,
                                                                      sender_mod_inst,
                                                                      l_mod_index,
                                                                      deployed_receiver_mod,
                                                                      receiver_mod_inst,
                                                                      receiver_link,
                                                                      sender_link)
                        l_mod_index += 1

                if w in protection_domain.external_wires_connection and len(
                        protection_domain.external_wires_connection[w]) > 0:
                    # if wire is connected with an other link outside the protection domaine
                    # => communication with TCP sockets
                    socket_interface_str=""
                    if w in protection_domain.wire_client_socket_index:
                        socket_index = protection_domain.wire_client_socket_index[w]
                        socket_interface_str = "&ctx->interface_ctx_array["+str(socket_index)+"]"
                    elif w in protection_domain.wire_server_socket_index:
                        # the first socket is with the main process ( +1 )
                        socket_index = protection_domain.wire_server_socket_index[w] + 1
                        socket_interface_str = "&ctx->interface_ctx_array[ctx->nb_client+"+str(socket_index)+"]"
                    else:
                        continue

                    # to create op ID
                    if l.source == deployed_mod.name:
                        interface_name = l.target
                        interface_op_name = l.target_operation
                    else:
                        interface_name = l.source
                        interface_op_name = l.source_operation

                    text_op_map += "    // socket to component: %s\n"%(interface_name)
                    text_op_map += ctx_str + ".local_socket_operations["+str(l_sock_index)+"].interface = "\
                                        +socket_interface_str+";\n"
                    text_op_map += ctx_str + ".local_socket_operations["+str(l_sock_index)+"].op_id = "\
                                        +w.name() + "__" + interface_op_name + ";\n"
                    if l.type == 'RR':
                        text_op_map += ctx_str + ".local_socket_operations["+str(l_sock_index)+"].RR_answer_op_activating = "\
                                        +str(l.activating_RR_answer).lower() + "; // RR answer property\n"
                        text_op_map += ctx_str + ".local_socket_operations["+str(l_sock_index)+"].RR_answer_op_index = %i; // in fifo_manager, operation %s\n"\
                                        % (sender_mod_inst.entry_links_index[op_name][0], op_name)

                    else:
                        text_op_map += ctx_str + ".local_socket_operations["+str(l_sock_index)+"].RR_answer_op_activating = false; // not a RR\n"
                        text_op_map += ctx_str + ".local_socket_operations["+str(l_sock_index)+"].RR_answer_op_index = 0; // not a RR\n"

                    l_sock_index += 1

            connected_external_PF_wires = l.find_connected_wires_link(comp.name, protection_domain.external_PF_wires.keys())

            for w in connected_external_PF_wires:
                if l.source == deployed_mod.name:
                    interface_op_name = l.target_operation
                else:
                    interface_op_name = l.source_operation

                socket_index = 1 + protection_domain.external_PF_sending_socket_index[w.PF_link_id]
                socket_interface_str = "&ctx->interface_ctx_array[ctx->nb_client+"+str(socket_index)+"]"
                text_op_map += "    // external platform socket throw PF wire: %s\n"%w.PF_link_id
                text_op_map += ctx_str + ".external_socket_operations["+str(l_PF_sock_index)+"].interface = "\
                                +socket_interface_str+";\n"
                text_op_map += ctx_str + ".external_socket_operations["+str(l_PF_sock_index)+"].op_id = "\
                                + w.name()+"__"+interface_op_name+";\n"

                if l.type == 'RR':
                    text_op_map += ctx_str + ".external_socket_operations["+str(l_sock_index)+"].RR_answer_op_activating = "\
                                    +str(l.activating_RR_answer).lower() + "; // RR answer property\n"
                    text_op_map += ctx_str + ".external_socket_operations["+str(l_sock_index)+"].RR_answer_op_index = %i; // RR answer\n"%sender_mod_inst.entry_links_index[op_name][0]
                else:
                    text_op_map += ctx_str + ".external_socket_operations["+str(l_sock_index)+"].RR_answer_op_activating = false; // not a RR\n"
                    text_op_map += ctx_str + ".external_socket_operations["+str(l_sock_index)+"].RR_answer_op_index = 0; // not a RR\n"

                l_PF_sock_index += 1

    text = generate_operation_map_allocation(ctx_str + ".", op_name, l_sock_index, l_mod_index, l_PF_sock_index,
                                             deployed_mod, op)
    text += text_op_map

    return text


def generate_operation_map_allocation(string_operation_map, operation_name, socket_num, module_num, PF_socket_num,
                                      deployed_mod, op):
    """@TODO Function docstring"""
    text = "\n\
    // operation #OP_NAME#:\n\
#CONTEXT#op_name = \"#OP_NAME#\";\n\
#CONTEXT#nb_module = #MODULE_NUM#;\n\
#CONTEXT#nb_local_socket = #SOCK_NUM#;\n\
#CONTEXT#nb_ext_socket = #EXTERN_SOCK_NUM#;\n\
\n\
#CONTEXT#module_operations = #CALLOC_MODULE#;\n\
#CONTEXT#local_socket_operations = #CALLOC_SOCKET#;\n\
#CONTEXT#external_socket_operations = #CALLOC_EXT_SOCKET#;\n"

    if module_num == 0:
        text = text.replace("#CALLOC_MODULE#", "NULL")
    else:
        text = text.replace("#CALLOC_MODULE#", "calloc(#MODULE_NUM#, sizeof(ldp_mod_operation))")

    if socket_num == 0:
        text = text.replace("#CALLOC_SOCKET#", "NULL")
    else:
        text = text.replace("#CALLOC_SOCKET#", "calloc(#SOCK_NUM#, sizeof(ldp_socket_operation))")

    if PF_socket_num == 0:
        text = text.replace("#CALLOC_EXT_SOCKET#", "NULL")
    else:
        text = text.replace("#CALLOC_EXT_SOCKET#", "calloc(#EXTERN_SOCK_NUM#, sizeof(ldp_socket_operation))")

    return text.replace("#OP_NAME#", operation_name)\
                .replace("#MODULE_NUM#", str(module_num))\
                .replace("#SOCK_NUM#", str(socket_num))\
                .replace("#EXTERN_SOCK_NUM#", str(PF_socket_num))\
                .replace("#CONTEXT#", string_operation_map)


def generate_mod_properties_ctx(context_string, mtype, minst, component, libraries):
    """@TODO Function docstring"""
    text = "    // Properties for module " + minst.name + "\n"
    if len(minst.property_values) > 0:
        text += "    " + context_string + ".properties = malloc(sizeof(" + mtype.name \
                + "__properties));\n"
        text += "    memcpy(" + context_string + ".properties, &((" + mtype.name \
                + "__properties){\n"
        for prop in minst.property_values.values():
            text += property_init_generate(prop, component, libraries)

        text += "       }), sizeof(" + mtype.name + "__properties));"

    return text


def generate_mod_pinfo_ctx(directory, context_string, mtype, minst, component):
    """@TODO Function docstring"""
    pinfo_num = len(mtype.private_pinfo + mtype.public_pinfo)
    text = "    // Pinfo manager\n"
    if pinfo_num > 0:
        text += context_string + ".pinfo_manager.pinfo_num =  " + str(pinfo_num) + ";\n"
        text += context_string + ".pinfo_manager.pinfo_array = calloc(" + str(
            pinfo_num) + ",sizeof(ldp_pinfo_struct));\n"
        for _, (pinfo_name, pinfo) in enumerate(minst.pinfo.items()):
            l_pinfo_value = pinfo.get_pinfo_value(component.properties).replace("\"","")
            l_pinfodir = os.path.join(directory, "Pinfo", os.path.dirname(l_pinfo_value))
            os.makedirs(l_pinfodir, exist_ok=True)

            l_pinfofile = os.path.join(pinfo.directory, l_pinfo_value)
            l_pinfofile = os.path.abspath(l_pinfofile)
            shutil.copy(l_pinfofile, l_pinfodir)

            pinfo_file = os.path.join("./Pinfo", l_pinfo_value)
            text += context_string + ".pinfo_manager.pinfo_array[" + str(
                pinfo.index) + "].filename = \""+pinfo_file+"\";// " + pinfo_name + "\n"
    else:
        text += context_string + ".pinfo_manager.pinfo_num = 0;\n"
    return text


def generate_sizeof_parameters(mod_type, op_name):
    text = ""

    if mod_type.operations[op_name].type in ['ARS', 'SRS']:
        input_params = False
    else:
        input_params = True


    if mod_type.operations[op_name].type in ['RR', 'ARS', 'SRS']:
        text += "2*sizeof(ECOA__uint32)+" # for RR ID and module client ID

    for param in mod_type.operations[op_name].params:
        if (param.direction == "input" and input_params) or\
           (param.direction == "output" and not input_params) :
            text+="sizeof(%s)+"%fix_C_data_type(param.type)

    if text == "":
        return "0"
    return text[:-1]


def generate_fifo_manager(context_string, pool_num, fifo_size):
    """@TODO Function docstring"""
    text = "\
    // Fifo manager\n\
#CONTEXT#.fifo_manager = malloc(sizeof(ldp_fifo_manager));\n\
#CONTEXT#.fifo_manager->fifo = malloc(sizeof(ldp_fifo));\n\
#CONTEXT#.fifo_manager->fifo->size = #FIFO_SIZE#;\n\
#CONTEXT#.fifo_manager->op_pool_num = #NUMBER_POOL#;\n\
#CONTEXT#.fifo_manager->op_element_pools = calloc(#NUMBER_POOL#, sizeof(ldp_element_pool));\n\
#CONTEXT#.fifo_manager->op_element_pools[0]" + ".element_num = 8; // lifecycle operations\n\
#CONTEXT#.fifo_manager->op_element_pools[0]" + ".parameter_size = 0; // no parameters\n"

    return text.replace("#FIFO_SIZE#", str(fifo_size)) \
               .replace("#CONTEXT#", context_string) \
               .replace("#NUMBER_POOL#", str(pool_num+1))# dont forget the pool reserved for lifecycle operation

fifo_pool_templ="\
#CONTEXT#.fifo_manager->op_element_pools[#POOL_INDEX#].element_num = #NUM_ELEMENT#; // #OP_NAME#\n\
#CONTEXT#.fifo_manager->op_element_pools[#POOL_INDEX#].parameter_size = #PARAM_SIZE#;\n"



def generate_fifo_manager_module(context_string, m_inst, fifo_size, mod_type, comp):
    text=""
    l_index = 0
    for op_name, (l_index, l) in sorted(m_inst.entry_links_index.items(), key=lambda x: x[1][0]):
        text += fifo_pool_templ.replace("#POOL_INDEX#", str(l_index)) \
                               .replace("#NUM_ELEMENT#", str(l.fifoSize)) \
                               .replace("#PARAM_SIZE#", generate_sizeof_parameters(mod_type, op_name)) \
                               .replace("#OP_NAME#", op_name)

    return text.replace("#CONTEXT#", context_string)


def generate_fifo_manager_dyn_trigger(context_string, d_inst):
    text=""
    for op_name, (l_index, l) in sorted(d_inst.entry_links_index.items(), key=lambda x: x[1][0]):
        # compute parameters size
        params_size_str=""
        if l_index == 1:
            # in operation
            params_size_str = "LDP_HEADER_TCP_SIZE"
            for param in d_inst.params:
                params_size_str += " + sizeof(" + fix_C_data_type(param.type) + ")"
        else:
            # reset operation
            params_size_str ="0"

        # generate pool
        text += fifo_pool_templ.replace("#POOL_INDEX#", str(l_index)) \
                               .replace("#NUM_ELEMENT#", str(l.fifoSize)) \
                               .replace("#PARAM_SIZE#", params_size_str) \
                               .replace("#OP_NAME#", op_name)

    return text.replace("#CONTEXT#", context_string)



def generate_mod_VD_manager(context_string, space, mod_inst, pd, comp):
    main_tmpl="\
#SPACE##CONTEXT_STRING#.num_reader_mng = #NUM_READER_MNG#; \n\
#SPACE##CONTEXT_STRING#.num_writter_mng = #NUM_WRITTER_MNG#;\n\
#SPACE##CONTEXT_STRING#.VD_reader_managers = #ALLOC_READER_MNG#;\n\
#SPACE##CONTEXT_STRING#.VD_writter_managers = #ALLOC_WRITTER_MNG#;\n"

    create_reader_mng_tmpl="\
#SPACE#ldp_create_reader_mng(&#CONTEXT_STRING#.VD_reader_managers[#READER_MNG_INDEX#]\
, &ctx->VD_repo_array[#VD_REPO_INDEX#], #NUM_READ_ACCESS#);//#OP_COMMENT#\n"

    create_writter_mng_tmpl="\
#SPACE#ldp_create_writter_mng(&#CONTEXT_STRING#.VD_writter_managers[#WRITTER_MNG_INDEX#]\
, &ctx->VD_repo_array[#VD_REPO_INDEX#], #NUM_WRITTEN_ACCESS#, #MODE#);//#OP_COMMENT#\n"

    text = main_tmpl
    # generate allocation of VD context:
    if(len(mod_inst.VD_read_op_map) == 0):
        text = text.replace("#ALLOC_READER_MNG#",'NULL')
    else:
        text = text.replace("#ALLOC_READER_MNG#", "calloc(#NUM_READER_MNG#, sizeof(ldp_VD_reader_mng))")

    if(len(mod_inst.VD_written_op_map) == 0):
        text = text.replace("#ALLOC_WRITTER_MNG#",'NULL')
    else:
        text = text.replace("#ALLOC_WRITTER_MNG#", "calloc(#NUM_WRITTER_MNG#, sizeof(ldp_VD_writter_mng))")

    # generate reader manager contexts:
    for operation, comp_impl_vd in mod_inst.VD_read_op_map.items():
        tmp_test = create_reader_mng_tmpl
        if comp_impl_vd != None:
            PD_VD_repo = pd.find_connected_vd_repo(comp, comp_impl_vd)
            tmp_test = tmp_test.replace("#VD_REPO_INDEX#", str(PD_VD_repo.pd_vd_index))\
                               .replace("#NUM_READ_ACCESS#", str(operation.maxVersions))
        else:
            # VD not connected
            tmp_test = tmp_test.replace("&ctx->VD_repo_array[#VD_REPO_INDEX#]", "NULL") \
                               .replace("#NUM_READ_ACCESS#", "0")

        text += tmp_test.replace("#READER_MNG_INDEX#", str(operation.module_VD_op_index))\
                        .replace("#OP_COMMENT#",operation.name)

    # generate written manager contexts:
    for operation, comp_impl_vd in mod_inst.VD_written_op_map.items():
        tmp_test = create_writter_mng_tmpl
        if comp_impl_vd != None:
            PD_VD_repo = pd.find_connected_vd_repo(comp, comp_impl_vd)
            tmp_test = tmp_test.replace("#VD_REPO_INDEX#", str(PD_VD_repo.pd_vd_index))
        else:
            # VD not connected
            tmp_test = tmp_test.replace("&ctx->VD_repo_array[#VD_REPO_INDEX#]", "NULL") \

        text += tmp_test.replace("#WRITTER_MNG_INDEX#", str(operation.module_VD_op_index))\
                        .replace("#NUM_WRITTEN_ACCESS#", str(operation.maxVersions))\
                        .replace("#OP_COMMENT#",operation.name)\
                        .replace("#MODE#", operation.mode)

    text = text.replace("#NUM_READER_MNG#", str(len(mod_inst.VD_read_op_map)))\
                 .replace("#NUM_WRITTER_MNG#", str(len(mod_inst.VD_written_op_map)))\
                 .replace("#CONTEXT_STRING#", context_string)\
                 .replace("#SPACE#", space)

    return text +"\n"



def generate_log_structure(ctx_str, deployed_mod, component, module_inst):
    """@TODO Function docstring"""
    if module_inst.name in component.mod_log_levels:
        log_levels_list = component.mod_log_levels[module_inst.name]
    else:
        log_levels_list = component.log_levels

    text = ""
    text += ctx_str + ".logger = malloc(sizeof(ldp_logger));\n"
    text += "    *(" + ctx_str + ".logger) = (ldp_logger) {\n" \
                                 "       ctx->logger->initializer,\n" \
                                 "       ctx->logger->config_filename,\n" \
                                 "       ctx->logger->name,\n" \
                                 "       \""+deployed_mod.component_name+"\",\n"\
                                 "       \""+deployed_mod.name+"\",\n"
    for i, log_level in enumerate(log_levels_list):
        if i > 0:
            text += "|"
        text += "ECOA_LOG_" + log_level
    text += "   };\n\n"
    return text

def generate_cpu_mask(ctx_str, deployed_mod, protection_domain):
    text = "    // CPU mask\n"
    if protection_domain.fine_grain_deployment == None:
        text += ctx_str+".cpu_affinity_mask = ldp_create_cpu_mask_full();\n"
        return text

    PD_deployment = protection_domain.fine_grain_deployment.get_protection_domain(protection_domain.name)

    if PD_deployment != None:
        dep_mod_affinity = PD_deployment.find_module_affinity(deployed_mod.name, deployed_mod.component_name)
        if dep_mod_affinity != None:
            cpu_IDs = sorted(dep_mod_affinity.core_ids)
        else:
            cpu_IDs = PD_deployment.default_cores
        cpu_nb = len(cpu_IDs)
        cpu_IDs_str = ",".join(cpu_IDs)

        text += ctx_str+".cpu_affinity_mask = ldp_create_cpu_mask("+str(cpu_nb)+", (int["+str(cpu_nb)+"]){"+cpu_IDs_str+"});\n"
    else:
        #select all cpu on node
        text += ctx_str+".cpu_affinity_mask = ldp_create_cpu_mask_full();\n"


    return text
