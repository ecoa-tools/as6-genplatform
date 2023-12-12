# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

from .driver_api_generator import os
from ecoa.utilities.logs import debug, error
from .operation_generator import generate_params_variable, generate_param_fct_call2,\
    generate_temporary_complex_params_variable, generate_temporary_param_fct_call2
from ..fix_names import fix_C_data_type, fix_C_libname
from ..version_header_generator import generate_ldp_version_header_warning
from collections import OrderedDict
from ..force_generation import file_need_generation


# from models import component_implementation

##################################
def generate_component_h(output_dir, comp_list, component_impl, force_flag):
    """@TODO Function docstring"""
    c_filename = output_dir + os.sep + "component_" + component_impl.get_name() + ".h"
    if not file_need_generation(c_filename,
                            force_flag,
                            "Component H file already exists for " + component_impl.get_name()):
        return

    fd = open(c_filename, 'w')
    text = generate_ldp_version_header_warning()
    text += "#ifndef _COMPONENT_" + component_impl.get_name().upper() + "_H \n"
    text += "#define _COMPONENT_" + component_impl.get_name().upper() + "_H \n\n"

    # define route macro
    text += "#include <apr_thread_proc.h>\n"
    text += "#include \"ldp_structures.h\"\n\n"

    for comp in comp_list:
        for module_i in component_impl.get_module_instances():
            text += "void* start_module_" + comp.name + "_" + module_i.name + "(apr_thread_t* t, " \
                                                                              "void* args);\n "

    # define initialise function for each component with this component implementation
    for comp in comp_list:
        text += "extern ldp_PDomain_ctx* " + comp.name + "_ctx;\n"
        text += "ldp_PDomain_ctx* init_comp_" + comp.name + "(void);\n"

    print(text, file=fd)

    print("#endif  /* _COMPONENT_" + component_impl.get_name().upper() + "_H */", file=fd)

    fd.close()


##################################
def generate_component_c(output_dir, comp_list, component_type, component_impl, wires, force_flag,
                         libraries):
    """@TODO Function docstring"""
    c_filename = output_dir + os.sep + "component_" + component_impl.get_name() + ".c"
    if not file_need_generation(c_filename,
                            force_flag,
                            "Component C file already exists for " + component_impl.get_name()):
        return

    fd = open(c_filename, 'w')

    #################################################
    ## header
    text = generate_ldp_version_header_warning()
    text += "#include <stdio.h> \n"
    text += "#include <stdlib.h>  \n"
    text += "#include <string.h> \n"
    text += "#include <assert.h> \n\n"

    text += "#include <apr.h>\n"
    text += "#include <apr_thread_cond.h>\n"
    text += "#include <apr_network_io.h>\n"
    text += "#include <apr_time.h>\n"
    text += "#include <apr_thread_proc.h>\n\n"

    text += "#include \"ldp_thread.h\"\n"
    text += "#include \"ldp_structures.h\"\n"
    text += "#include \"route.h\"\n"
    text += "#include \"ldp_network.h\"\n"
    text += "#include \"ldp_comp_util.h\"\n"
    text += "#include \"ldp_trigger.h\"\n"
    text += "#include \"ldp_dynamic_trigger.h\"\n\n"
    text += "#include \"ldp_log.h\"\n"
    text += "#include \"ldp_log_platform.h\"\n"
    text += "#include \"ldp_dynamic_trigger.h\"\n"
    text += "#include \"ldp_mod_container_util.h\"\n"
    text += "#include \"ldp_mod_lifecycle.h\"\n"
    text += "#include \"ldp_fifo_manager.h\"\n"
    text += "#include \"ldp_VD.h\"\n"
    text += "#include \"component_" + component_impl.get_name() + ".h\"\n"
    text += "#include \"component_" + component_impl.get_name() + "__properties.h\"\n"

    for _, module in component_impl.get_module_implementations().items():
        text += "#include \"" + module.get_name() + "_container.h\" \n"
        text += "#include \"" + module.get_name() + ".h\" \n\n"

    print(text, file=fd)

    #########################################
    ### generate module start functions
    for comp in comp_list:
        for module_i in component_impl.get_module_instances():
            text = generate_module_start_fct(comp, component_impl, module_i, libraries, component_type, wires)
            print(text, file=fd)

    fd.close()


def generate_properties_API(output_dir, comp_list, component_type, component_impl, libraries, force_flag):
    """@TODO Function docstring"""
    filename = output_dir + os.sep + "component_" + component_impl.get_name() + "__properties.h"

    if not file_need_generation(filename,
                            force_flag,
                            "Component properties file already exists for " + component_impl.get_name()):
        return

    fd = open(filename, 'w')
    print(generate_ldp_version_header_warning(), file=fd)

    for lib in libraries.keys():
        print("#include \"" + fix_C_libname(lib) + ".h\"", file=fd)

    for mtype in component_impl.module_types.values():
        text = "// property struct\n"
        text += "typedef struct " + mtype.name + "__properties {\n"
        for prop in mtype.properties.values():
            text += "    " + fix_C_data_type(prop.get_type()) + " "
            text += prop.name + ";\n"
        text += "} " + mtype.name + "__properties;\n"
        print(text, file=fd)

    text = "// component properties\n"
    text += "typedef struct " + component_type.name + "__properties{\n"
    for prop in component_type.properties.values():
        text += "    " + fix_C_data_type(prop.type) + " "
        text += prop.name + ";\n"
    text += "} " + component_type.name + "__properties;\n"
    print(text, file=fd)

    fd.close()


def generate_module_start_fct(comp, component_impl, module_i, libraries, component_type, wires):
    """@TODO Function docstring"""
    module_impl = component_impl.get_module_implementations()[module_i.get_implementation()]
    mtype = component_impl.get_module_type(module_impl.type)

    text = "\n void * start_module_" + comp.name + "_" + module_i.name \
           + "(apr_thread_t* t, void* args){\n"

    text += "   ldp_module_context* ctx = (ldp_module_context*) args;\n"
    text += "   " + module_i.get_implementation() + "__context module_impl;\n"
    text += "   module_impl.platform_hook = (struct " + module_i.get_implementation() + "__platform_hook*)ctx;\n\n"
    text += "   ctx->mem_pool = apr_thread_pool_get(t);\n"
    text += "   ldp_init_pinfo_manager(&ctx->pinfo_manager, ctx->logger_PF);\n"
    text += "   ldp_init_mod_VD_managers(ctx);\n"

    # if a asynchronous Request Resqponse operation exists for this module
    first_op_async = next((op for op in mtype.operations.values() if op.type == 'ARS'), None)
    if first_op_async is not None:
        text += "// start a dynamic trigger thread to remove sent asynchronous RR that are out of " \
                "date\n "
        text += "   apr_thread_t* RR_dyn_trigger_thread;\n"
        text += "   ldp_mod_start_RR_trigger( ctx, &RR_dyn_trigger_thread);\n\n"

    text += "   ldp_element* elt;\n"

    text += "    bool is_running = true;\n"
    text += "    while(is_running){\n"
    text += "       ldp_fifo_manager_pop_elt(ctx->fifo_manager, &elt);\n"

    text += "       switch (elt->op_ID){\n"
    text += "       case LDP_ID_INITIALIZE_life:\n"
    text += "           if(ctx->state == IDLE){\n"
    text += "               " + module_i.get_implementation() + "__INITIALIZE__received(" \
                                                                "&module_impl);\n "
    text += "               ldp_mod_lifecycle_initialize(ctx);\n"
    text += "           }else{\n"
    text += "               ldp_log_PF_log(ECOA_LOG_WARN_PF,\"WARNING\", ctx->logger_PF,\"[" \
            "               " + module_i.name + "]: received INIT. Invalid state\");\n"
    text += "               ldp_send_fault_error_to_father(ctx->component_ctx, ctx->mod_id, \
ECOA__asset_type_COMPONENT, ECOA__error_type_INITIALISATION_PROBLEM, 5);\n"
    text += "           }\n"
    text += "           break;\n"
    text += "       case LDP_ID_START_life:\n"
    text += "           if(ctx->state == READY){\n"
    text += "               ldp_mod_lifecycle_start(ctx);\n"
    text += "               " + module_i.get_implementation() + "__START__received(&module_impl);\n"
    text += "           }else{\n"
    text += "               ldp_log_PF_log(ECOA_LOG_WARN_PF,\"WARNING\", ctx->logger_PF,\"[" \
            "               " + module_i.name + "]: received START. Invalid state\");\n"
    text += "               ldp_send_fault_error_to_father(ctx->component_ctx, ctx->mod_id,\
ECOA__asset_type_COMPONENT, ECOA__error_type_INITIALISATION_PROBLEM, 6);\n"
    text += "           }\n"
    text += "           break;\n"
    text += "       case LDP_ID_STOP_life:\n"
    text += "           if(ctx->state == RUNNING){\n"
    text += "               " + module_i.get_implementation() + "__STOP__received(&module_impl);\n"
    text += "               ldp_mod_lifecycle_stop(ctx);\n"
    text += "           }else{\n"
    text += "               ldp_log_PF_log(ECOA_LOG_WARN_PF,\"WARNING\", ctx->logger_PF,\"[" \
            "               " + module_i.name + "]: received STOP. Invalid state\");\n"
    text += "           }\n"
    text += "           break;\n"
    text += "       case LDP_ID_SHUTDOWN_life:\n"
    text += "           if (ctx->state == RUNNING || ctx->state == READY){\n"
    text += "               " + module_i.get_implementation() + "__SHUTDOWN__received(" \
                                                                "&module_impl);\n "
    if first_op_async is not None:
        text += "               ldp_mod_lifecycle_shutdown(ctx, RR_dyn_trigger_thread);\n"
    else:
        text += "               ldp_mod_lifecycle_shutdown(ctx, NULL);\n"
    text += "           }else{\n"
    text += "               ldp_log_PF_log(ECOA_LOG_WARN_PF,\"WARNING\", ctx->logger_PF,\"[" \
            "               " + module_i.name + "]: received SHUTDOWN. Invalid state\");\n"
    text += "           }\n"
    text += "           break;\n"
    text += "       case LDP_ID_KILL_life:\n"
    text += "           " + module_i.get_implementation() + "__SHUTDOWN__received(&module_impl);\n"
    if first_op_async is not None:
        text += "           ldp_mod_lifecycle_kill(ctx, RR_dyn_trigger_thread);\n"
    else:
        text += "           ldp_mod_lifecycle_kill(ctx, NULL);\n"
    text += "           is_running = false;\n"
    text += "           break;\n"
    text += "       default:\n"
    text += "            if(ctx->state != RUNNING){\n"
    text += "                ldp_log_PF_log_var(ECOA_LOG_WARN_PF,\"WARN\", ctx->logger_PF,\"[" \
            "                " + module_i.name + "] Module is not in RUNNING state. Erase msg " \
                                                 "%u\",elt->op_ID);\n "
    text += "               ldp_send_fault_error_to_father(ctx->component_ctx, ctx->mod_id, ECOA__asset_type_COMPONENT, ECOA__error_type_UNAVAILABLE, 2);\n"
    text += "            }"

    space = "                "

    for op_index, op_name in enumerate(module_i.entry_points_dict.keys()):
        op = mtype.operations[op_name]
        op_id_used = OrderedDict()  # to avoid double op_id
        real_op_id_used = OrderedDict()  # to avoid double op_id
        for _, l in enumerate(module_i.entry_points_dict[op_name]):
            # to avoid double op_id
            if l.get_op_id() in op_id_used:
                continue
            op_id_used[l.get_op_id()] = 1

            l_op_id = comp.name + "__" + module_i.name + "__"+ op_name
            if l_op_id in real_op_id_used:
                continue
            real_op_id_used[l_op_id] = 1

            # nothing to to for synchronise_response_send operation because this is done after
            # the sent of the request (in the client module_impl container)
            if op.type == 'SRS':
                continue

            # nothing to do for data operation
            if op.type in ['DW', 'DR']:
                # nothing to generate
                continue

            text += "else if( elt->op_ID == " + comp.name + "__" + module_i.name + "__" \
                    + op_name
            if op.type == 'ARS' and not l.is_between_modules(component_impl):
                ## RR trigger for timeout uses the op_ID that has been used on the network
                ## and not the module local op_ID for this operation.

                wire = comp.find_connected_wires__source_service(wires, l.target)
                if wire is not None:
                    text += " ||\n" + space + "       elt->op_ID == "
                    text += wire.name() + "__"
                    text += l.target_operation + " // used for ELI-msg or RR-timeout-msg (from RR trigger)\n    " + space
                else:
                    # not connected wire for this operation
                    pass

            text += "){ //" + str(l) + "\n"

            if op.type == "ER" or op.type == "ES":
                text += generate_params_variable(op, "0", with_input=True,
                                                 with_output=True)
                text += space + module_impl.get_name() + "__" + op.name + "__received(&module_impl"
                text += generate_param_fct_call2(op, with_input=True, with_output=True)
                text += ");\n"

            elif op.type == 'RR':
                start_read_index = "sizeof(ECOA__uint32) "
                text += space + "ECOA__uint32 ID;\n"
                text += space + "memcpy(&ID, &elt->parameters[0]," \
                                "sizeof(ECOA__uint32));\n"
                text += generate_params_variable(op, start_read_index, with_input=True,
                                                 with_output=False)

                text += space + "if(ldp_check_concurrent_RR_num(ctx," + \
                        str(op.RR_op_index) + ", " + \
                        str(op.maxVersions) + ") == MOD_CONTAINER_OK){\n"
                text += space + "    ctx->req_resp.current_RR_number[" + str(
                    op.RR_op_index) + "]++;\n"

                text += space + module_impl.get_name() + "__" + op.name + "__request_received(" \
                                                                          "&module_impl, ID "
                text += generate_param_fct_call2(op, with_input=True)
                text += ");\n"

                text += "}\n"

            elif op.type == 'ARS':
                text += space + "ECOA__uint32 ID;\n"
                text += space + "memcpy(&ID, &elt->parameters[0],sizeof(" \
                                "ECOA__uint32));\n\n "
                text += space + "// update the concurrent number of this RR\n"
                text += space + "ctx->req_resp.current_RR_number[" + str(
                    op.RR_op_index) + "]--;\n"
                text += generate_params_variable(op,
                                                 "sizeof(ECOA__uint32)",
                                                 with_input=False, with_output=True)

                text += space + "if(ID != ECOA__UINT32_MAX){\n"
                text += space + "    // if it is a real reponse:\n"
                text += space + "    ldp_node* node;\n"
                text += space + "    if(ldp_find_req_sent(&ctx->req_resp,ID, &node) != NULL){\n"
                text += space + "        ldp_free_req_sent(&ctx->req_resp,node);\n"

                text += space + "        " + module_impl.get_name() + "__" + op.name \
                        + "__response_received(&module_impl, ID,ECOA__return_status_OK "
                text += generate_param_fct_call2(op, with_output=True) + ");\n"

                text += space + "    }else{\n"
                text += space + "ldp_log_PF_log(ECOA_LOG_WARN_PF,\"WARN\", ctx->logger_PF, " \
                                "\"In comp " + component_impl.name + " and module " + \
                        module_i.name + ": sent RR not found\");\n "
                text += space + "        ID = ECOA__UINT32_MAX;\n"
                text += space + "    }\n"
                text += space + "}\n"
                text += space + "if(ID == ECOA__UINT32_MAX){\n"
                text += space + "    // if it is not a real reponse:\n"
                # Declare temporary variables to handle the not real response
                text += generate_temporary_complex_params_variable(op,
                                                                   "sizeof(ECOA__uint32)",
                                                                   with_input=False, with_output=True)
                for param in op.params:
                    if param.direction == 'output':
                        param_type_lib, param_type_name = param.type.split(':')
                        if param_type_lib == 'ECOA' and param_type_name == 'boolean8':
                            text += space + "    " + param.name + "= ECOA__FALSE;\n"
                        else:
                            if not param.is_complex:
                                text += space + "    memset("
                                text += "&" + param.name
                                text += ",0 ,sizeof(" + fix_C_data_type(param.type) + "));\n"

                text += space + "    " + module_impl.get_name() + "__" + op.name \
                        + "__response_received(&module_impl, ID,ECOA__return_status_NO_RESPONSE "
                text += generate_temporary_param_fct_call2(op, with_output=True) + ");\n"

                text += space + "}\n"
            elif op.type == 'DRN':
                text += space + "// notification\n"
                text += space + module_impl.get_name() + "__" + op.name \
                        + "__updated(&module_impl);\n"

            else:
                error("In component " + component_impl.name + ": operation of type " + op.type + " not supported")
                text += " // " + component_impl.name + ": operation of type " + op.type + " not supported\n"
            text += "            }"

    text += "else{\n"
    text += "               ldp_log_PF_log_var(ECOA_LOG_WARN_PF,\"WARN\", ctx->logger_PF,\"[" \
            + module_i.name + "] unknow msg %u\",elt->op_ID);assert(0);\n"
    text += "               ldp_send_fault_error_to_father(ctx->component_ctx, ctx->mod_id,\
ECOA__asset_type_COMPONENT, ECOA__error_type_UNAVAILABLE, 3);\n"
    text += "           }\n"
    text += "		}\n"
    text += "           ldp_fifo_manager_release_elt(ctx->fifo_manager, elt);\n"
    text += "	}\n"

    text += "   ldp_destroy_pinfo_manager(&ctx->pinfo_manager);\n"

    # text += "    destroy_mod_VD_manager(&ctx->VD_manager);\n"
    text += "return NULL;\n}\n\n"

    return text
