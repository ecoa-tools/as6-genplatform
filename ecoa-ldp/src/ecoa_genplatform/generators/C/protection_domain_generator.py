# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

import os
from collections import OrderedDict
from .module_ctx_generator import generate_generic_mod_context, \
                                  generate_normal_mod_context, \
                                  generate_trigger_mod_context, \
                                  generate_dyn_trigger_mod_context
from ecoa.utilities.logs import info, debug, error
from ..version_header_generator import generate_ldp_version_header_warning
from ..force_generation import file_need_generation


from .operation_generator import fix_C_data_type

##
## @brief      Generate all protection domains functions
##
## @param      directory           The directory where to write files
## @param      protection_domains  The dictionary of protection domains
## @param      components          The dictionary of components
##
## @return
##
def generate_all_protection_domains(directory, protection_domains, components,
                                    component_implementations, wires, component_types,
                                    service_definitions, libraries, platform_links, current_platform,
                                    force_flag):
    """ Generate all protection domains functions
    """
    for pd in protection_domains.values():
        generate_protection_domain_c(directory, protection_domains, pd, components, component_implementations, wires,
                                     component_types, service_definitions, libraries, platform_links,
                                     current_platform, force_flag)

def generate_protection_domain_c(directory, protection_domains, protection_domain, components,
                                 component_implementations, wires, component_types, service_definitions,
                                 libraries, platform_links, current_platform, force_flag):
    """Generate C functions of a protection domain:
        * main function
        * message router function
    """
    info(" # Generate C file for PD "+protection_domain.name)
    filename = os.path.join(directory, "PD_" + protection_domain.get_name() + ".c")

    if not file_need_generation(filename,
                            force_flag,
                            "    Protection domain main file already exists for " + protection_domain.get_name()):
        return

    comp_list = set()
    for module in protection_domain.deployed_modules:
        if module.component_name not in comp_list:
            comp_list.add(module.component_name)
    comp_list = list(comp_list)


    fd = open(filename, 'w')
    text = generate_ldp_version_header_warning()
    text += "#include \"ldp_fine_grain_deployment.h\" // Need to be first to define _GNU_SOURCE\n"
    text += "#include <stdio.h>\n"
    text += "#include <inttypes.h>\n"
    text += "#include <assert.h>\n"
    text += "#include <apr.h>\n"
    text += "#include <apr_time.h>\n"
    text += "#include \"ldp_thread.h\"\n"
    text += "#include \"ldp_structures.h\"\n\n"
    text += "#include \"ldp_log.h\"\n"
    text += "#include \"route.h\"\n"
    text += "#include \"ldp_dynamic_trigger.h\"\n"
    text += "#include \"ldp_trigger.h\"\n"

    text += "#include \"ldp_comp_util.h\"\n"
    text += "#include \"ldp_network.h\"\n"
    text += "#include \"ldp_mod_container_util.h\"\n"
    text += "#include \"ldp_ELI_udp.h\"\n"

    text += "#include \"ldp_fifo_manager.h\"\n"
    for svc_name in sorted(service_definitions):
        text += "#include \"svc_"+svc_name+"_deserial.h\"\n"

    for comp_impl_name in protection_domain.get_all_component_implementations_name(components):
        comp_impl_tmp,_ = component_implementations[comp_impl_name]
        if comp_impl_tmp.has_cpp_module():
            text += "#include \"component_"+comp_impl_name+".hpp\"\n"
        else:
            text += "#include \"component_"+comp_impl_name+".h\"\n"
        text += "#include \"component_" + comp_impl_name + "__properties.h\"\n"

    for comp_name in protection_domain.get_all_component_names():
        text += "ldp_PDomain_ctx* "+comp_name+"_ctx = NULL;\n"

    text += generate_router_function(protection_domain, component_implementations, components,
                                     component_types, service_definitions, platform_links)
    text += generate_buffer_size_computation_fct(protection_domains,
                                                 protection_domain, components,
                                                 component_implementations)

    text += "\nint main(void){\n"
    text += "    apr_initialize();\n"
    text += "    apr_pool_t* mem_pool;\n"
    text += "    apr_pool_create(&mem_pool,NULL);\n\n"

    text += protection_domain_ctx_gen(directory, protection_domain, components, component_implementations,
                                      wires, libraries, component_types, current_platform, platform_links)

    text += "    ldp_destroy_component(ctx);\n"
    text += "    apr_pool_destroy(mem_pool);\n"

    text += "    ldp_log_shutdown();\n"
    text += "    apr_terminate();\n"
    text += "}\n"

    print(text, file=fd)
    fd.close()

def protection_domain_ctx_gen(directory, pd, components, component_implementations, wires, libraries,
                              component_types, current_platform, platform_links):
    """Generate context C code of a protection domain"""
    text = "    /// Initialisation of protection domain context " + pd.name + "\n"
    text += "    ldp_status_t ret;\n"
    text += "    ldp_PDomain_ctx* "+"ctx = malloc(sizeof(ldp_PDomain_ctx));\n"

    for comp_name in pd.get_all_component_names():
        text += "    "+comp_name+"_ctx = ctx;\n"
    text += "    ctx->name = \"" + pd.name + "\"; \n"
    text += "    ctx->mem_pool = mem_pool;\n"
    text += "    ctx->route_function_ptr = &router_socket_msg_" + pd.name + ";\n"
    text += "    ctx->sched_policy = LDP_SCHED_"+pd.get_scheduler_policy()+";\n"
    if current_platform != None:
        text += "    ctx->ELI_platform_ID = ELI_PF_"+current_platform.name+";\n"

    # Loggers
    text += "    // loggers\n"
    text += "    ctx->logger = malloc(sizeof(ldp_logger));\n"
    text += "    ctx->logger->config_filename = \"log_"+pd.name+".properties\";\n"
    text += "    ldp_log_init(ctx->logger);\n"
    text += "    ldp_log_initialize(ctx->logger,ctx->name);\n\n"

    text += "    ctx->logger_PF = malloc(sizeof(ldp_logger_platform));\n"
    text += "    ctx->logger_PF->config_filename = \"log_"+pd.name+"_PF.properties\";\n"
    text += "    ldp_log_PF_initialize(ctx->logger_PF,\""+pd.name+"_PF\");\n"
    text += "    ctx->logger_PF->pd_name = \""+pd.name+"\";\n"
    text += "    ctx->logger_PF->node_name = \"_\";\n"
    text += "    ctx->logger_PF->level_mask=0xffff;\n"

    # fine grain deployment of the technical thread
    text += "\n    // technical thread affinity\n"
    text += generate_technical_cpu_affinity(pd.fine_grain_deployment, "ctx->logger_PF")

    ## Buffer pool
    text += "\n"
    text += "    ctx->msg_buffer_size = "+pd.name+"_compute_buffer_size();\n"

    l_nb_client = len(pd.wire_client_socket_index)
    l_nb_server = len(pd.wire_server_socket_index) + len(pd.external_PF_sending_socket_index) + 1
    l_client_offset = 0
    l_server_offset = 0

    # sockets
    # TODO WARNING only work if modules of component are deployed in the same PD
    text += "    ctx->nb_client = " + str(l_nb_client) + "; \n"
    text += "    ctx->nb_server = " + str(l_nb_server) + "; \n"
    text += "    ctx->interface_ctx_array = calloc(ctx->nb_client+ctx->nb_server, " \
            "sizeof(ldp_interface_ctx));\n"

    text += "    ctx->interface_ctx_array[" + str(l_nb_client) + "].type = LDP_LOCAL_IP;\n"
    text += "    ctx->interface_ctx_array[" + str(l_nb_client) + "].info_r = (ldp_tcp_info) {" + pd.name + "_port, " + pd.name \
            + "_addr, 1, true}; // socket with main process. Does not match with a wire\n"

    template_server_port="\
    ctx->interface_ctx_array[ctx->nb_client+#INDEX#].type = #INTERFACE_TYPE#;\n\
    ctx->interface_ctx_array[ctx->nb_client+#INDEX#].info_r = (ldp_tcp_info) {#WIRE_NAME#_port,\n\
                                            #WIRE_NAME#_addr,\n\
                                            #NUM_BUFFER#, true};\n"


    template_client_port="\
    ctx->interface_ctx_array[#INDEX#].type = #INTERFACE_TYPE#;\n\
    ctx->interface_ctx_array[#INDEX#].info_r = (ldp_tcp_info) {#WIRE_NAME#_port,\n\
                                            #WIRE_NAME#_addr,\n\
                                            #NUM_BUFFER#, false};\n"

    template_ELI_port="\
    ctx->interface_ctx_array[ctx->nb_client+#INDEX#].type = LDP_ELI_MCAST;\n\
    ctx->interface_ctx_array[ctx->nb_client+#INDEX#].info_r = (ldp_tcp_info) {#WIRE_NAME#_sent_port,\n\
                                            #WIRE_NAME#_sent_addr,\n\
                                            #NUM_BUFFER#, false};\n\
    ctx->interface_ctx_array[ctx->nb_client+#INDEX#].inter.mcast.UDP_current_PF_ID = #WIRE_NAME#_sent_PF_ID;\n\
    ctx->interface_ctx_array[ctx->nb_client+#INDEX#].inter.mcast.link_num = 1;\n\
    ctx->interface_ctx_array[ctx->nb_client+#INDEX#].inter.mcast.PF_links_ctx = calloc(1, sizeof(ldp_PF_link));\n\
    ctx->interface_ctx_array[ctx->nb_client+#INDEX#].inter.mcast.PF_links_ctx[0] = (ldp_PF_link){\n\
        {ELI_PF_#CONNECTED_PF_NAME#, #WIRE_NAME#_read_PF_ID, #CHANNEL_NUM#, #BUFFER_SIZE#,\n\
        (ldp_ELI_UDP_channel[#CHANNEL_NUM#]){}},NULL};\n"

    template_ELI_read_socket="\
    ctx->mcast_read_interface[#INDEX#].type = LDP_ELI_MCAST;\n\
    ctx->mcast_read_interface[#INDEX#].info_r = (ldp_tcp_info) {#LINK_NAME#_read_port,\n\
                                            #LINK_NAME#_read_addr,\n\
                                            #NUM_BUFFER#, false};\n\
    ctx->mcast_read_interface[#INDEX#].inter.mcast.link_num = #LINK_NUM#;\n\
    ctx->mcast_read_interface[#INDEX#].inter.mcast.PF_links_ctx = calloc(#LINK_NUM#, sizeof(ldp_PF_link));\n"

    template_read_ELI_link_ctx="\
    ctx->mcast_read_interface[#INDEX#].inter.mcast.PF_links_ctx[#LINK_INDEX#] = (ldp_PF_link){\n\
        {ELI_PF_#CONNECTED_PF_NAME#, #WIRE_NAME#_read_PF_ID, #CHANNEL_NUM#, 0, NULL},\n\
        &ctx->interface_ctx_array[ctx->nb_client+#SENT_INTER_INDEX#]};\n\
    ctx->mcast_read_interface[#INDEX#].inter.mcast.PF_links_ctx[#LINK_INDEX#].link_ctx.buffer_size = #BUFFER_SIZE#;\n\
    ldp_initialized_PF_link(&ctx->mcast_read_interface[#INDEX#].inter.mcast.PF_links_ctx[#LINK_INDEX#].link_ctx);\n"

    normal_deployed_module = pd.get_normal_deployed_module(components, component_implementations)
    dynamic_deployed_module = pd.get_dynamic_trigger_deployed_module(components,
                                                                     component_implementations)
    trigger_deployed_module = pd.get_trigger_deployed_module(components, component_implementations)

    for wire, w_index in pd.wire_server_socket_index.items():
        buf_counter = wire.count_written_modules_num(True, components, component_implementations)
        # +1 because the first interface is for the main process
        text += template_server_port.replace("#INDEX#", str(w_index+1))\
                       .replace("#INTERFACE_TYPE#", "LDP_LOCAL_IP")\
                       .replace("#WIRE_NAME#", wire.name())\
                       .replace("#NUM_BUFFER#", str(buf_counter))

    for wire, w_index in pd.wire_client_socket_index.items():
        buf_counter = wire.count_written_modules_num(False, components, component_implementations)
        text += template_client_port.replace("#INDEX#", str(w_index))\
                       .replace("#INTERFACE_TYPE#", "LDP_LOCAL_IP")\
                       .replace("#WIRE_NAME#", wire.name())\
                       .replace("#NUM_BUFFER#", str(buf_counter))

    # ELI written Sockets
    for pf_link_id, l_index in pd.external_PF_sending_socket_index.items():
        pf_link = platform_links[pf_link_id]
        # +1 because the first interface is for the main process
        text += template_ELI_port.replace("#INDEX#", str(l_index+1))\
                                 .replace("#WIRE_NAME#", pf_link_id)\
                                 .replace("#NUM_BUFFER#", str(0))\
                                 .replace("#CHANNEL_NUM#", str(1))\
                                 .replace("#BUFFER_SIZE#", str(0))\
                                 .replace("#CONNECTED_PF_NAME#", pf_link.get_other_platform(current_platform.name))

    # ELI read Sockets
    # for l_index, pf_link_id in enumerate(pd.external_PF_sending_socket_index.keys()):
    mcast_read_interface_num = len(pd.external_PF_reading_socket_index)
    text += "    ctx->mcast_read_interface_num = " + str(mcast_read_interface_num) + "; \n"
    if mcast_read_interface_num > 0:
        text += "    ctx->mcast_read_interface = calloc("+str(mcast_read_interface_num)+", " \
                "sizeof(ldp_interface_ctx));\n"
    for l_index, pf_link_IDs in enumerate(pd.external_PF_reading_socket_index.values()):
        tmp_text = template_ELI_read_socket

        for pf_link_index, pf_link_id in enumerate(pf_link_IDs):
            pf_link = platform_links[pf_link_id]
            sent_inter_index = pd.external_PF_sending_socket_index[pf_link_id]+1 # +1 because the first interface is for the main process
            buffer_size_str = ""

            for ii,ll in enumerate(pf_link.service_syntax):
                if (ii == 0):
                    buffer_size_str = "min_buffer_size_"+ll.name+"()"
                else:
                    buffer_size_str = "ldp_max(min_buffer_size_"+ll.name+"(),"+buffer_size_str+")"

            tmp_text += template_read_ELI_link_ctx.replace("#LINK_INDEX#", str(pf_link_index))\
                                                  .replace("#CONNECTED_PF_NAME#", pf_link.get_other_platform(current_platform.name))\
                                                  .replace("#WIRE_NAME#", pf_link_id)\
                                                  .replace("#CHANNEL_NUM#", str(pf_link.link_binding.find_max_channel(current_platform.name)))\
                                                  .replace("#BUFFER_SIZE#", str(buffer_size_str))\
                                                  .replace("#SENT_INTER_INDEX#", str(sent_inter_index))

        # chose the ID name of the first PF_link_ID (because all PF_links have the same values of address and port)
        text += tmp_text.replace("#INDEX#", str(l_index))\
                        .replace("#LINK_NAME#", pf_link_IDs[0])\
                        .replace("#NUM_BUFFER#", str(0))\
                        .replace("#LINK_NUM#", str(len(pf_link_IDs)))


    ## modules context allocation
    text += "\n    //init module instances context \n"
    text += "    ctx->nb_module = " + str(len(normal_deployed_module)) + ";\n"
    if len(normal_deployed_module) > 0:
        text += "    apr_threadattr_t* mod_attr[ctx->nb_module];\n"
        text += "    apr_thread_t* mod_thread[ctx->nb_module];\n"
        text += "    ctx->worker_context = calloc(ctx->nb_module, sizeof(ldp_module_context));\n"

    text += "\n    //init trigger instances context \n"
    text += "    ctx->nb_trigger = " + str(len(trigger_deployed_module)) + ";\n"
    if len(trigger_deployed_module) > 0:
        text += "    apr_threadattr_t* trig_attr[ctx->nb_trigger];\n"
        text += "    apr_thread_t* trig_thread[ctx->nb_trigger];\n"
        text += "    ctx->trigger_context = calloc(ctx->nb_trigger, " \
                "sizeof(ldp_trigger_context));\n"

    text += "\n    //init dynamic trigger instances context \n"
    text += "    ctx->nb_dyn_trigger = " + str(len(dynamic_deployed_module)) + ";\n"
    if (len(dynamic_deployed_module)) > 0:
        text += "    apr_threadattr_t* dyn_trig_attr[ctx->nb_dyn_trigger];\n"
        text += "    apr_thread_t* dyn_trig_thread[ctx->nb_dyn_trigger];\n"
        text += "    ctx->dyn_trigger_context = calloc(ctx->nb_dyn_trigger, " \
                "sizeof(ldp_dyn_trigger_context));\n\n"


    text += generate_VD_repository(pd, "    ")

    ## Modules context
    for d_m in normal_deployed_module:
        text += generate_generic_mod_context("    ctx->worker_context["+str(d_m.index)+"]",
                                             pd, d_m, components)
        text += generate_normal_mod_context(directory, "    ctx->worker_context["+str(d_m.index)+"]",
                                            pd, d_m, components, component_implementations, wires, libraries,
                                            component_types)
        text += "\n"

    for d_m in trigger_deployed_module:
        text += generate_generic_mod_context("    ctx->trigger_context["+str(d_m.index)+"]", pd,
                                             d_m, components)
        text += generate_trigger_mod_context("    ctx->trigger_context["+str(d_m.index)+"]", pd,
                                             d_m, components, component_implementations, wires,
                                             component_types)
        text += "\n"

    for d_m in dynamic_deployed_module:
        text += generate_generic_mod_context("    ctx->dyn_trigger_context["+str(d_m.index)+"]",
                                             pd, d_m, components)
        text += generate_dyn_trigger_mod_context("    ctx->dyn_trigger_context["+str(d_m.index)+"]",
                                                 pd, d_m, components, component_implementations,
                                                 wires, component_types)
        text += "\n"

    text += genereate_VD_repository_readers(pd, wires, component_implementations, "    ")

    # buffer
    text += "    ldp_comp_init_state(ctx);\n"
    text += "    ldp_init_VD_repositories(ctx);\n"

    thread_attr_str = ""
    if len(normal_deployed_module) > 0:
        thread_attr_str += " mod_attr"
    else:
        thread_attr_str += " NULL"

    if len(dynamic_deployed_module) > 0:
        thread_attr_str += ", dyn_trig_attr"
    else:
        thread_attr_str += ", NULL"

    if len(trigger_deployed_module) > 0:
        thread_attr_str += ", trig_attr"
    else:
        thread_attr_str += ", NULL"
    text += "    ldp_comp_prepare_module_threads(ctx,"+thread_attr_str+");\n"
    text += "    ldp_thread_properties prop = {.policy=ctx->sched_policy, .logger=ctx->logger_PF};\n"

    for dyn_trig_mod in dynamic_deployed_module:
        text += "    prop.priority = ctx->dyn_trigger_context["+ str(dyn_trig_mod.index) + "].priority;\n"
        text += "    prop.thread_name = ctx->dyn_trigger_context[" + str(dyn_trig_mod.index) + "].name;\n"
        text += "    prop.cpu_affinity_mask = ctx->dyn_trigger_context[" + str(dyn_trig_mod.index) + "].cpu_affinity_mask;\n"

        text += "    ret=ldp_thread_create(&dyn_trig_thread[" + str(dyn_trig_mod.index) + "], " \
                +"dyn_trig_attr[" + str(dyn_trig_mod.index) + "], " \
                +"ldp_start_module_dynamic_trigger, " +"(void*) &ctx->dyn_trigger_context[" \
                + str(dyn_trig_mod.index) + "], &prop," \
                +"ctx->mem_pool);\n"
        text += "    if (ret != APR_SUCCESS) {\n\
        ldp_send_fault_error_to_father(ctx, ctx->dyn_trigger_context["+ str(dyn_trig_mod.index) + "].mod_id,\
ECOA__asset_type_COMPONENT, ECOA__error_type_INITIALISATION_PROBLEM, 1);\n\
    }\n"
        text += "    assert(ret==APR_SUCCESS);\n\n"

    # start module thread with specific module start function and context
    for trig_mod in trigger_deployed_module:
        text += "    prop.priority = ctx->trigger_context["+ str(trig_mod.index) + "].priority;\n"
        text += "    prop.thread_name = ctx->trigger_context[" + str(trig_mod.index) + "].name;\n"
        text += "    prop.cpu_affinity_mask = ctx->trigger_context[" + str(trig_mod.index) + "].cpu_affinity_mask;\n"

        text += "    ret=ldp_thread_create(&trig_thread[" + str(trig_mod.index) + "], " \
                +"trig_attr[" + str(trig_mod.index) + "], " \
                +"ldp_start_module_trigger, (void*) &ctx->trigger_context[" \
                + str(trig_mod.index) + "], " +"&prop, ctx->mem_pool);\n"
        text += "    if (ret != APR_SUCCESS) {\n\
        ldp_send_fault_error_to_father(ctx, ctx->trigger_context["+ str(trig_mod.index) + "].mod_id, \
ECOA__asset_type_COMPONENT, ECOA__error_type_INITIALISATION_PROBLEM, 2);\n\
    }\n"
        text += "    assert(ret==APR_SUCCESS);\n\n"

    for d_m in normal_deployed_module:
        text += "    prop.priority = ctx->worker_context["+ str(d_m.index) + "].priority;\n"
        text += "    prop.thread_name = ctx->worker_context[" + str(d_m.index) + "].name;\n"
        text += "    prop.cpu_affinity_mask = ctx->worker_context[" + str(d_m.index) + "].cpu_affinity_mask;\n"

        text += "    ret=ldp_thread_create(&mod_thread["+str(d_m.index)+"],mod_attr["\
                +str(d_m.index)+"],start_module_" +d_m.component_name+"_"+d_m.name\
                +", (void*) &ctx->worker_context["+str(d_m.index)+"], &prop,ctx->mem_pool);\n"
        text += "    if (ret != APR_SUCCESS) {\n\
        ldp_send_fault_error_to_father(ctx, ctx->worker_context["+ str(d_m.index) + "].mod_id, \
ECOA__asset_type_COMPONENT, ECOA__error_type_INITIALISATION_PROBLEM, 4);\n\
    }\n"
        text += "    assert(ret==APR_SUCCESS);\n\n"

    text += "\n    ldp_start_comp_server(ctx);\n"

    thread_list_str = ""
    if len(normal_deployed_module) > 0:
        thread_list_str += " mod_thread"
    else:
        thread_list_str += " NULL"

    if len(dynamic_deployed_module) > 0:
        thread_list_str += ", dyn_trig_thread"
    else:
        thread_list_str += ", NULL"

    if len(trigger_deployed_module) > 0:
        thread_list_str += ", trig_thread"
    else:
        thread_list_str += ", NULL"
    text += "    ldp_wait_modules(ctx,"+thread_list_str+");\n"

    text += "    UNUSED(ret);\n"

    return text


def generate_buffer_size_computation_fct(protection_domains, protection_domain, components, component_implementations):
    """Generate function to compute size of buffer of a protection domain"""
    l_params_size_list = generate_buffer_size_params_size_list(protection_domain, components, component_implementations)

    return generate_buffer_size_text(protection_domain.name, sorted(l_params_size_list))


def generate_buffer_size_params_size_list(protection_domain, components, component_implementations):
    """Compute the params_size list of a protection domain for function to compute size of buffer"""
    list_mod_type = set()
    for dep_mod in protection_domain.get_normal_deployed_module(components,
                                                                component_implementations):
        comp = components[dep_mod.component_name]
        comp_impl, _ = component_implementations[comp.component_implementation]
        mod_type = comp_impl.find_module_type(dep_mod.name)
        list_mod_type.add(mod_type)

    params_size_list = set()
    # generatate param string for module
    for m_type in list_mod_type:
        for operation in m_type.operations.values():
            param_size = ""
            if operation.type in ['ARS', 'RR', 'SRS']:
                param_size = "12"

            for param in operation.params:
                if param_size != "":
                    param_size += "+"
                param_size += "sizeof("+fix_C_data_type(param.type) +")"
            if param_size != "":
                #if param_size not in params_size_list:
                params_size_list.add(param_size)

    # generatate param string for dynamic trigger
    for dyn_dep_mod in protection_domain.get_dynamic_trigger_deployed_module(
            components, component_implementations):
        comp = components[dyn_dep_mod.component_name]
        comp_impl, _ = component_implementations[comp.component_implementation]
        dyn_inst = comp_impl.get_instance(dyn_dep_mod.name)
        param_size = "sizeof(ECOA__duration*)"
        for param in dyn_inst.params:
            param_size += "+ sizeof("+fix_C_data_type(param.type) +")"
        params_size_list.add(param_size)

    return params_size_list

def generate_buffer_size_text(pd_name, params_size_list):
    """Generate function to compute size of buffer of a protection domain"""
    # generate function
    text = "static int "+pd_name+"_compute_buffer_size(void){\n"
    if len(params_size_list) == 0:
        text += "int size_of_buffer = 0;\n"
    else:
        text += "int size_of_buffer = -1;\n"
        text += "int tmp;\n"
        for p_size in params_size_list:
            text += "tmp = "+p_size + ";\n"
            text += "size_of_buffer = ( tmp < size_of_buffer ) ? size_of_buffer : tmp;\n"
    text += "\n   return size_of_buffer+LDP_ELI_HEADER_SIZE+28;\n}\n"
    return text


def generate_router_function(protection_domain, component_implementations, components,
                             component_types, service_definitions, platform_links):
    """Generate function to route message"""

    router_function_tpl ="\
static void router_socket_msg_#PD_NAME#(ldp_PDomain_ctx* ctx, uint32_t operation_id, char* params,\n\
                                        int params_size, ldp_interface_ctx* socket_sender, int port_nb, uint32_t ELI_sequence_num, ECOA__uint32 sender_PF_ID){\n\
\n\
    uint32_t mod_op_id = 0;\n\
    //char* msg_buffer = params;\n\
    \n\
    #SOCKET_SWITCHES#\
    {\n\
        ldp_log_PF_log_var(ECOA_LOG_WARN_PF,\"WARN\", ctx->logger_PF,\n\
                            \"[PD %s] wrong port number %i, op: %i, PF id: %i\",\n\
                            ctx->name, port_nb, operation_id, sender_PF_ID);\n\
    }\n\
\n\
    UNUSED(mod_op_id);\n\
    UNUSED(params);\n\
    UNUSED(params_size);\n\
    UNUSED(socket_sender);\n\
}\n\n"

    switch_socket_tpl="\
#SPACE#switch (operation_id){\n\
#CASE#\
#SPACE#default:\n\
#SPACE#    ldp_log_PF_log_var(ECOA_LOG_WARN_PF,\"WARN\", ctx->logger_PF,\n\
#SPACE#    \"[PD %s] wrong operation ID %i on port number %i, from PF id %i\",\n\
#SPACE#     ctx->name, operation_id, port_nb, sender_PF_ID);\n\
#SPACE#}\n"

    deserialized_tmpl = "\
#SPACE#// need to write parameters as a local TCP message\n\
#SPACE#params_size = deserialized_#SYNTAX_NAME#_#SERVICE_OP_NAME##REQUEST_SUFFIX#"+\
                                            "(ctx->msg_buffer, params);\n"

    text = ""
    space_str="        "

    # wires in the Platform
    for wire in protection_domain.external_wires_connection.keys():
        if len(protection_domain.external_wires_connection[wire]) > 0:
            tmp_str = ""
            interface_ctx_index_str = ""
            service_syntax = wire.find_service_syntax(components, component_types, service_definitions)

            # if the wire has a connection outside the protection domain as a client
            if wire in protection_domain.wire_client_socket_index:
                # if wire has a connection outside as a client
                socket_index = protection_domain.wire_client_socket_index[wire]
                interface_ctx_index_str = str(socket_index)
                serv_ref_name = wire.target_service
                receiver_comp_name = wire.target_component
                input_serv_op_names = service_syntax.find_input_operation(True)

            # if wire has a connection outside the protection domain as a server
            if wire in protection_domain.wire_server_socket_index:
                # the first socket is with the main process ( +1 below )
                socket_index = protection_domain.wire_server_socket_index[wire] + 1
                interface_ctx_index_str = "ctx->nb_client + "+str(socket_index)
                serv_ref_name = wire.source_service
                receiver_comp_name = wire.source_component
                input_serv_op_names = service_syntax.find_input_operation(False)

            ## generate router for this interface:
            comp = components[receiver_comp_name]
            comp_impl, _ = component_implementations[comp.component_implementation]
            # for each service operation that can handle this interface :
            for service_op_name in input_serv_op_names:
                tmp_str += space_str+"case " + wire.name() + "__" + service_op_name + ":{\n"

                tmp_str += generate_wire_router_case(wire, protection_domain,
                                                     service_syntax.find_operation(service_op_name),
                                                     serv_ref_name, comp,
                                                     comp_impl, True, "", False)

                tmp_str += space_str +"    break;\n"
                tmp_str += space_str +"}\n"

            if tmp_str != "":
                text += "if (port_nb == ctx->interface_ctx_array["+interface_ctx_index_str+"].info_r.port){\n"
                text += switch_socket_tpl.replace("#SPACE#","        ").replace("#CASE#", tmp_str)
                text += "    }else "

    ### ELI case
    for binding_file, PF_link_ID_list in protection_domain.external_PF_reading_socket_index.items():
        # for PF_link_id, service_syntax_names in protection_domain.ELI_input_operations.items():
        tmp_str_binding=""
        for PF_link_id in PF_link_ID_list:
            tmp_str=""
            service_syntax_names = protection_domain.ELI_input_operations[PF_link_id]

            for service_syntax_name, operation_names in service_syntax_names.items():
                service_syntax,_ = service_definitions[service_syntax_name]
                tmp_str+= space_str+"// input operations for syntax "+service_syntax.name+"\n"

                tmp_str += generate_ELI_syntax_router_case(protection_domain,
                                                            service_syntax,
                                                            components,
                                                            component_implementations,
                                                            operation_names,
                                                            deserialized_tmpl,
                                                            space_str)

            if tmp_str != "":
                tmp_str_binding += space_str + "// ========= link : "+ PF_link_id+"\n" + tmp_str

        if tmp_str_binding != "":
            text += "if ("
            text += "(port_nb == "+PF_link_id+"_read_port) && (\n"
            for index, pf_link_id in enumerate(PF_link_ID_list):
                text += "      (sender_PF_ID == "+pf_link_id+"_read_PF_ID) "
                if (index != len(PF_link_ID_list)-1):
                    text += "||\n"
            text += ")"
            text +="){\n"
            text += switch_socket_tpl.replace("#SPACE#","        ").replace("#CASE#", tmp_str_binding)
            text += "    }else "

    return router_function_tpl.replace("#PD_NAME#", protection_domain.name)\
                              .replace("#SOCKET_SWITCHES#", text)

def generate_ELI_syntax_router_case(protection_domain,
                    service_syntax, components, component_implementations,
                    operation_names, deserialized_tmpl, space_str):
    tmp_str = ""
    for serv_op_name, wires in operation_names.items():

        if wires == []:
            continue

        serv_op = service_syntax.find_operation(serv_op_name)
        deserialized_str = deserialized_tmpl.replace("#SYNTAX_NAME#",service_syntax.name)\
                                                .replace("#SERVICE_OP_NAME#", serv_op_name)
        PD_is_client = (wires[0].target_component in protection_domain.get_all_component_names())

        tmp_str += space_str+"    case "+wires[0].name()+"__"+serv_op_name+":\n"
        for w in wires:
             tmp_str += space_str+"    // wire "+w.name()+"\n"
        tmp_str += space_str+"{\n"

        if serv_op.nature in ['CMD','NOTIFY']:
            last_wire = False
            for i,w in enumerate(wires):
                if i>0:
                    # no need to deserialize message more than one time
                    deserialized_str = ""
                if i == len(wires)-1:
                    last_wire = True

                if PD_is_client:
                    receiver_comp_name = w.target_component
                    serv_ref_name = w.target_service
                else:
                    receiver_comp_name = w.source_component
                    serv_ref_name = w.source_service

                comp = components[receiver_comp_name]
                comp_impl, _ = component_implementations[comp.component_implementation]

                tmp_str += generate_wire_router_case(w, protection_domain, serv_op, serv_ref_name,
                                                     comp, comp_impl, last_wire, deserialized_str, True)
        elif serv_op.nature in ['RR']:
            if PD_is_client:
                # server of an RR
                receiver_comp_name = wires[0].target_component
                serv_ref_name = wires[0].target_service
            else:
                receiver_comp_name = wires[0].source_component
                serv_ref_name = wires[0].source_service

            comp = components[receiver_comp_name]
            comp_impl, _ = component_implementations[comp.component_implementation]

            tmp_str += generate_wire_router_case(wires[0], protection_domain, serv_op, serv_ref_name,
                                                 comp, comp_impl, True, deserialized_str, True)

        else:
            tmp_str += generate_update_VD_repo_init(space_str+"    ", \
                                                    deserialized_str.replace("#REQUEST_SUFFIX#",""))
            for w in wires:
                if PD_is_client:
                    receiver_comp_name = w.target_component
                    serv_ref_name = w.target_service
                else:
                    receiver_comp_name = w.source_component
                    serv_ref_name = w.source_service

                comp = components[receiver_comp_name]
                tmp_str += generate_update_VD_repository(protection_domain, comp, space_str+"    ",
                                                        serv_ref_name, serv_op.name, True)
            tmp_str += generate_update_VD_repo_end(space_str+"    ")
        tmp_str += space_str +"    break;\n"
        tmp_str += space_str +"}\n"
    return tmp_str

def generate_wire_router_case(wire, protection_domain, service_op, sev_ref_name, comp,
                                comp_impl, last_wire, deserialized_str, is_ELI_case):


    # last_wire : an other wire could be connected to this service operation. Other links may need to be generated
    #                   Is used only for event operation to manage buffer copy
    event_tmpl="\
#SPACE#mod_op_id = #COMP_NAME#__#MOD_NAME#__#OP_NAME#;\n\
#SPACE#// event for module #MOD_NAME#\n\
#SPACE#ldp_comp_received_event(ctx, #BUFFER_COPY_BOOL#, params, params_size,\n\
#SPACE#                          &ctx->worker_context[#MOD_INDEX#], #OP_INDEX_LINK#, #ACTIVATED_LINK#, mod_op_id);\n"

    event_eli_tmpl="\
#SPACE#mod_op_id = #COMP_NAME#__#MOD_NAME#__#OP_NAME#;\n\
#SPACE#// event for module #MOD_NAME#\n\
#SPACE#ldp_comp_received_event(ctx, #BUFFER_COPY_BOOL#, ctx->msg_buffer, params_size,\n\
#SPACE#                          &ctx->worker_context[#MOD_INDEX#], #OP_INDEX_LINK#, #ACTIVATED_LINK#, mod_op_id);\n"

    request_response_tmpl="\
#SPACE#// response of RR #OP_NAME#\n\
#SPACE#mod_op_id = #COMP_NAME#__#MOD_NAME#__#OP_NAME#;\n\
#SPACE#memcpy(&ELI_sequence_num, params, sizeof(ECOA__uint32));\n\
#SPACE#ldp_comp_received_answer_request(ctx,\n\
#SPACE#                                   &params[sizeof(ECOA__uint32)], // only parameters + ID\n\
#SPACE#                                   params_size - sizeof(ECOA__uint32),// parameters : without ELI_sequence_num\n\
#SPACE#                                   ELI_sequence_num, mod_op_id);\n"

    request_response_eli_tmpl="\
#SPACE#// response of RR #OP_NAME#\n\
#SPACE#ldp_comp_received_answer_request(ctx,\n\
#SPACE#                                   ctx->msg_buffer, // parameters + ID\n\
#SPACE#                                   params_size,// parameters : without ELI_sequence_num\n\
#SPACE#                                   ELI_sequence_num, operation_id);\n"

    request_eli_tmpl="\
#SPACE#// request #OP_NAME# for module #MOD_NAME#\n\
#SPACE#mod_op_id = #COMP_NAME#__#MOD_NAME#__#OP_NAME#;\n\
#SPACE#//change op_id for specific module router\n\
#SPACE#ldp_comp_received_request(ctx,\n\
#SPACE#                            ctx->msg_buffer, // parameters and request ID\n\
#SPACE#                            params_size,\n\
#SPACE#                            &ctx->worker_context[#MOD_INDEX#],\n\
#SPACE#                            socket_sender,\n\
#SPACE#                            ELI_sequence_num,\n\
#SPACE#                            #ANSWER_OP_ID#,\n\
#SPACE#                            #OP_INDEX_LINK#, #ACTIVATED_LINK#, mod_op_id);\n"

    request_tmpl="\
#SPACE#// request #OP_NAME# for module #MOD_NAME#\n\
#SPACE#mod_op_id = #COMP_NAME#__#MOD_NAME#__#OP_NAME#;\n\
#SPACE#//change op_id for specific module router\n\
#SPACE#memcpy(&ELI_sequence_num, params, sizeof(ECOA__uint32)); //load sender ID in eli_sequence_num\n\
#SPACE#ldp_comp_received_request(ctx,\n\
#SPACE#                            &params[sizeof(ECOA__uint32)], // only parameters + ID\n\
#SPACE#                            params_size - sizeof(ECOA__uint32),// parameters : without ELI_sequence_num\n\
#SPACE#                            &ctx->worker_context[#MOD_INDEX#],\n\
#SPACE#                            socket_sender,\n\
#SPACE#                            ELI_sequence_num,\n\
#SPACE#                            #ANSWER_OP_ID#,\n\
#SPACE#                            #OP_INDEX_LINK#, #ACTIVATED_LINK#, mod_op_id);\n"

    text = ""
    space_str = "            "
    op_nature = service_op.nature


    if op_nature == 'DATA':
        text += generate_update_VD_repo_init(space_str, deserialized_str.replace("#REQUEST_SUFFIX#",""))
        text += generate_update_VD_repository(protection_domain, comp,
                                              space_str, sev_ref_name, service_op.name, is_ELI_case)
        text += generate_update_VD_repo_end(space_str)

    elif op_nature in  ['CMD', 'NOTIFY', 'RR']:
        link_list = comp_impl.find_connected_links2(sev_ref_name, service_op.name)

        # if no connection
        if len(link_list) == 0:
            return text

        # for each links connected to this service operation
        for i,l in enumerate(link_list):
            if sev_ref_name == l.source and service_op.name == l.source_operation:
                module_inst = comp_impl.get_instance(l.target)
                module_op = comp_impl.find_module_type(module_inst.name).operations[l.target_operation]
            elif sev_ref_name == l.target and service_op.name == l.target_operation:
                module_inst = comp_impl.get_instance(l.source)
                module_op = comp_impl.find_module_type(module_inst.name).operations[l.source_operation]
            else:
                assert(0)
            deployed_mod = protection_domain.find_deployed_module(module_inst.name, comp.name)

            # generate code for an operation module
            if module_op.type in ["ER", "ES"]:
                if (i == len(link_list) - 1) and last_wire:
                    # last link and last wire
                    # use the buffer : no need to copy it in a new one
                    buffer_need_cpy = "false"
                else:
                    buffer_need_cpy = "true"
                text += deserialized_str.replace("#REQUEST_SUFFIX#","")
                if is_ELI_case:
                    text += event_eli_tmpl.replace("#BUFFER_COPY_BOOL#",buffer_need_cpy)
                else:
                    text += event_tmpl.replace("#BUFFER_COPY_BOOL#",buffer_need_cpy)
                break_loop = False

            elif module_op.type in ['ARS', 'SRS']:
                text += deserialized_str.replace("#REQUEST_SUFFIX#","_answer")
                if is_ELI_case:
                    text += request_response_eli_tmpl
                    # text += "#SPACE#memcpy(&ELI_sequence_num, &msg_buffer[LDP_HEADER_TCP_SIZE], sizeof(ECOA__uint32));\n"
                else:
                    text += request_response_tmpl
                break_loop = True # only on time

            elif module_op.type == 'RR':
                text += deserialized_str.replace("#REQUEST_SUFFIX#","_request")
                if is_ELI_case:
                    text += request_eli_tmpl.replace("#ANSWER_OP_ID#", wire.name()+"__"+service_op.name)
                else:
                    #text += "#SPACE#memcpy(&ELI_sequence_num, msg_buffer, sizeof(ECOA__uint32));\n"
                    text += request_tmpl.replace("#ANSWER_OP_ID#", wire.name()+"__"+service_op.name)
                break_loop = True # only on time

            else:
                error("Unknow module opearation type "+ module_op.type)

            text = text.replace("#COMP_NAME#", comp.name)\
                       .replace("#MOD_NAME#", module_inst.name)\
                       .replace("#OP_NAME#",module_op.name)\
                       .replace("#MOD_INDEX#", str(deployed_mod.index))\
                       .replace("#OP_INDEX_LINK#", str(module_inst.entry_links_index[module_op.name][0]))\
                       .replace("#ACTIVATED_LINK#",str(l.activating_op).lower())
            if break_loop:
                break
    else:
        # unknown nature
        error("Unknow module opearation nature "+ op_nature)
        assert(0)

    return text.replace("#SPACE#", space_str)


def generate_update_VD_repo_init(space, deserialized_str):
    update_VD_init_tmpl = "\
#SPACE#ldp_repository_VD* repo;UNUSED(repo);\n\
#SPACE#ECOA__return_status ret;UNUSED(ret);\n\
#SPACE#if (params_size != 0){\n\
#DESERIALIZE_STR#\n\
"
    return update_VD_init_tmpl.replace("#DESERIALIZE_STR#", deserialized_str)\
                              .replace("#SPACE#", space)

def generate_update_VD_repository(pd, comp, space, reference_name, op_name, ELI_case):
    update_VD_tmpl = "\
#SPACE#// Update a VD repository;\n\
#SPACE#repo = &ctx->VD_repo_array[#VD_INDEX#];\n\
#SPACE#ret = ldp_update_repository(repo, (unsigned char*) #DATA_VARIABLE#);\n\
#SPACE#if (ret != ECOA__return_status_OK){\n\
#SPACE#    ldp_log_PF_log_var(ECOA_LOG_WARN_PF,\"WARN\", ctx->logger_PF,\n\
#SPACE#        \"[PD %s] impossible to update a repository: index #VD_INDEX#, error : %i\", ctx->name, ret);\n\
#SPACE#}\n\
#SPACE#// notify readers module\n\
#SPACE#ldp_notify_local_readers(ctx, repo);\n\n"

    if ELI_case:
        data_var = "ctx->msg_buffer";
    else:
        data_var = "params";
    # find all vd repo to update
    text = ""
    for vd_repo in pd.VD_repositories:
        for vd_comp, comp_impl_vd in vd_repo.list_comp_impl_VD:
            # check if vd_repo is in the right component and if it has thre right ref and operation
            if comp == vd_comp and vd_repo.is_writter(reference_name,op_name, vd_comp.name):
                text += update_VD_tmpl.replace("#VD_INDEX#", str(vd_repo.pd_vd_index)) \
                                      .replace("#DATA_VARIABLE#", data_var)
    if text == "":
        text = "#SPACE#// no writter \n"

    return text.replace("#SPACE#", space)

def generate_update_VD_repo_end(space):
    update_VD_end_tmpl = "\
#SPACE#}\n"
    return update_VD_end_tmpl.replace("#SPACE#", space)

def generate_VD_repository(pd, space):
    VD_repo_tmpl = "#SPACE#// VD repositories\n\
#SPACE#ctx->num_VD_repo = #NUM_VD_REPO#;\n\
#SPACE#ctx->VD_repo_array = calloc(#NUM_VD_REPO#,sizeof(ldp_repository_VD));\n"

    VD_repo_create_tmpl ="\
#SPACE#ldp_create_repository(&ctx->VD_repo_array[#VD_REPO_INDEX#], \
#NUM_READERS#, #NUM_WRITTEN_COPY#,  sizeof(#VD_REPO_TYPE#), #MODE#, mem_pool);\n\
ctx->VD_repo_array[#VD_REPO_INDEX#].serial_data_fct = #SERIAL_FCT#;\n"

    if (len(pd.VD_repositories) == 0):
        text = space+"ctx->num_VD_repo = 0;\n"
        text +=space+"ctx->VD_repo_array = NULL;\n\n"
        return text

    text = VD_repo_tmpl
    for vd_repo in pd.VD_repositories:
        text +=  VD_repo_create_tmpl.replace("#VD_REPO_INDEX#", str(vd_repo.pd_vd_index)) \
                                    .replace("#NUM_READERS#", str(vd_repo.num_notified_readers)) \
                                    .replace("#NUM_WRITTEN_COPY#", str(vd_repo.num_written_copies)) \
                                    .replace("#VD_REPO_TYPE#", fix_C_data_type(vd_repo.get_vd_datatype()))\
                                    .replace("#MODE#", vd_repo.get_vd_access_mode())\
                                    .replace("#SERIAL_FCT#", vd_repo.serialisation_fct_name)

    text = text.replace("#SPACE#", space) \
               .replace("#NUM_VD_REPO#", str(len(pd.VD_repositories)))
    return text+"\n"

def genereate_VD_repository_readers(pd, wires, comp_implementations, space):
    text = ""
    if (len(pd.VD_repositories) == 0):
        return text

    reader_module_tmpl="\
#SPACE#ctx->VD_repo_array[#VD_REPO_INDEX#].readers[#READER_INDEX#].nature = MODULE;\n\
#SPACE#ctx->VD_repo_array[#VD_REPO_INDEX#].readers[#READER_INDEX#].reader_ptr = &ctx->worker_context[#DEP_MOD_INDEX#];\n\
#SPACE#ctx->VD_repo_array[#VD_REPO_INDEX#].readers[#READER_INDEX#].operation_id = #OP_ID#; //#OP_COMMENT#\n\
#SPACE#ctx->VD_repo_array[#VD_REPO_INDEX#].readers[#READER_INDEX#].mod_op_activating = #OP_ACTIVATING#;\n\
#SPACE#ctx->VD_repo_array[#VD_REPO_INDEX#].readers[#READER_INDEX#].mod_op_index = #OP_INDEX#;\n"

    reader_local_socket_tmpl="\
#SPACE#ctx->VD_repo_array[#VD_REPO_INDEX#].readers[#READER_INDEX#].nature = LOCAL_SOCKET;\n\
#SPACE#ctx->VD_repo_array[#VD_REPO_INDEX#].readers[#READER_INDEX#].reader_ptr = &ctx->interface_ctx_array[#SOCK_INDEX#];\n\
#SPACE#ctx->VD_repo_array[#VD_REPO_INDEX#].readers[#READER_INDEX#].operation_id = #OP_ID#; //#OP_COMMENT#\n"

    reader_local_repo_tmpl="\
#SPACE#ctx->VD_repo_array[#VD_REPO_INDEX#].readers[#READER_INDEX#].nature = REPOSITORY_VD;\n\
#SPACE#ctx->VD_repo_array[#VD_REPO_INDEX#].readers[#READER_INDEX#].reader_ptr = &ctx->VD_repo_array[#REPO_INDEX#];\n"

    reader_extern_socket_tmpl="\
#SPACE#ctx->VD_repo_array[#VD_REPO_INDEX#].readers[#READER_INDEX#].nature = EXTERN_SOCKET;\n\
#SPACE#ctx->VD_repo_array[#VD_REPO_INDEX#].readers[#READER_INDEX#].reader_ptr = &ctx->interface_ctx_array[ctx->nb_client+#SOCK_INDEX#];\n\
#SPACE#ctx->VD_repo_array[#VD_REPO_INDEX#].readers[#READER_INDEX#].operation_id = #OP_ID#; //#OP_COMMENT#\n"

    text += "// repository readers structures \n"
    for vd_repo in pd.VD_repositories:
        new_reader_str = ""
        reader_index = 0
        for comp, comp_impl_VD in vd_repo.list_comp_impl_VD:
            new_reader_str+="//"+comp.name+"\n"
            comp_impl,_ = comp_implementations[comp.component_implementation]
            # comp_impl_VD = vd_repo.comp_impl_VD

            for mod_reader in vd_repo.notified_modules[comp.name]:
                dep_mod = pd.find_deployed_module(mod_reader.name, comp.name)
                mod_inst = comp_impl.get_instance(mod_reader.name)
                op_index = mod_inst.entry_links_index[mod_reader.op_name][0]
                op_id = dep_mod.component_name + "__" + dep_mod.name + "__" + mod_reader.op_name
                new_reader_str += reader_module_tmpl.replace("#DEP_MOD_INDEX#", str(dep_mod.index))\
                                                .replace("#OP_INDEX#", str(op_index))\
                                                .replace("#OP_ACTIVATING#", str(mod_reader.activating_op).lower())\
                                                .replace("#OP_ID#", op_id) \
                                                .replace("#READER_INDEX#", str(reader_index))\
                                                .replace("#OP_COMMENT#", mod_reader.op_name)
                reader_index+=1

            for wire, reader in vd_repo.notified_local_sockets[comp.name]:
                socket_index = pd.wire_client_socket_index[wire]
                op_id = wire.name()+ "__" + reader.op_name
                new_reader_str += reader_local_socket_tmpl.replace("#SOCK_INDEX#", str(socket_index))\
                                                        .replace("#OP_ID#", op_id) \
                                                        .replace("#READER_INDEX#", str(reader_index))\
                                                        .replace("#OP_COMMENT#", reader.op_name)
                reader_index+=1

        # local PD repositories
        for wire, reader in vd_repo.notified_local_repo:
            new_reader_str += reader_local_repo_tmpl.replace("#REPO_INDEX#",str(reader.pd_vd_index))\
                                                    .replace("#READER_INDEX#", str(reader_index))
            reader_index+=1

        # external PF readers
        for wire, reader, pf_link_id in vd_repo.notified_ext_sockets:
            socket_index = pd.external_PF_sending_socket_index[pf_link_id]+1 #because of interface with main process
            op_id = wire.name()+ "__" + reader.op_name
            new_reader_str += reader_extern_socket_tmpl.replace("#SOCK_INDEX#", str(socket_index))\
                                                       .replace("#READER_INDEX#", str(reader_index))\
                                                       .replace("#OP_ID#", op_id) \
                                                       .replace("#OP_COMMENT#", reader.op_name)
            reader_index+=1

        text += new_reader_str.replace("#VD_REPO_INDEX#", str(vd_repo.pd_vd_index))+"\n"

    return text.replace("#SPACE#", space)


def generate_technical_cpu_affinity(fine_grain_deployment, logger_str):
    text=""
    if fine_grain_deployment != None:
        node_name =fine_grain_deployment.technical_cores[0].node_name
        platform_name = fine_grain_deployment.technical_cores[0].platform_name
        text += "    /* chose node "+node_name+" on "+platform_name+" */\n"
        core_ids = [c.core_id for c in fine_grain_deployment.technical_cores \
                    if c.platform_name == platform_name and c.node_name == node_name]
        nb_cpu = len(core_ids)
        core_ids_str = ",".join(core_ids)

        text += "    ctx->technical_cpu_mask = ldp_create_cpu_mask("+str(nb_cpu)+", (int["+str(nb_cpu)+"]){"+core_ids_str+"});\n"
        text += "    ret = ldp_set_proc_affinty(ctx->technical_cpu_mask);\n"
        text += "    if (ret != LDP_SUCCESS){\n"
        text += "        ldp_log_PF_log(ECOA_LOG_WARN_PF,\"WARNING\", "+logger_str+",\"Enable to set CPU affinity of main process\");\n"
        text += "    }\n"
    else:
        text += "    /* chose every cores on the node */\n"
        text += "    /* No need tyo set affinity: every cores are enable by default */\n"
        text += "    ctx->technical_cpu_mask = ldp_create_cpu_mask_full();\n"
    text += "    log_thread_deployment_properties(ctx->logger_PF);\n\n"
    return text
