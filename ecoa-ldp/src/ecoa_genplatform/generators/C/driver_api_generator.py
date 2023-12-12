# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

import os
from .operation_generator import generate_memcpy_parameters, generate_header_fct
from ..version_header_generator import generate_ldp_version_header_warning
from ecoa.utilities.logs import debug, error
from ..fix_names import fix_C_data_type, fix_C_libname
from ..force_generation import file_need_generation


def generate_external_h(output_dir, component_impl, force_flag, libraries):
    """@TODO Function docstring"""
    if not component_impl.has_external_c_links():
        return

    filename = component_impl.get_name() + "_External_Interface.h"
    c_filename = output_dir + os.sep + filename
    if not file_need_generation(c_filename,
                            force_flag,
                            "External Interface H file already exists for " + component_impl.get_name()):
        return

    fd = open(c_filename, 'w')
    print(generate_ldp_version_header_warning(), file=fd)
    print("/**", file=fd)
    print("* @file " + filename, file=fd)
    print("* External C Interface header for Component Implementation", file=fd)
    print("* " + component_impl.get_name(), file=fd)
    print("*/\n", file=fd)
    print("\n", file=fd)
    print("#ifdef __cplusplus\n", file=fd)
    print("extern \"C\" {\n", file=fd)
    print("#endif\n", file=fd)

    print("#ifndef " + component_impl.get_name().upper() + "_EXTERNAL_INTERFACE_H_", file=fd)
    print("#define " + component_impl.get_name().upper() + "_EXTERNAL_INTERFACE_H_ \n", file=fd)
    print("#include \"ECOA.h\"\n\n", file=fd)

    text = ""

    for library in libraries:
        text += "#include \"" + fix_C_libname(library) + ".h\"\n"

    externals_done = []
    for link in component_impl.get_links():
        if link.is_external_c() and link.source_operation not in externals_done:
            prototype = generate_external_prototype(component_impl, link)
            text += prototype + ";\n\n"
            externals_done.append(link.source_operation)

    print(text, file=fd)

    print("#endif\n", file=fd)

    print("#ifdef __cplusplus\n", file=fd)
    print("}\n", file=fd)
    print("#endif\n", file=fd)

    fd.close()


def generate_external_c(output_dir, protection_domains, component_impl, components, force_flag):
    """@TODO Function docstring"""
    if not component_impl.has_external_c_links():
        return

    filename = component_impl.get_name() + "_External_Interface.c"
    c_filename = output_dir + os.sep + filename
    if not file_need_generation(c_filename,
                            force_flag,
                            "External Interface C file already exists for " + component_impl.get_name()):
        return

    fd = open(c_filename, 'w')
    print(generate_ldp_version_header_warning(), file=fd)
    print("/**", file=fd)
    print("* @file " + filename, file=fd)
    print("* External C Interface implementation for Component Implementation", file=fd)
    print("* " + component_impl.get_name(), file=fd)
    print("*/\n", file=fd)
    print("#include \"ldp_structures.h\"", file=fd)
    print("#include \"ldp_mod_container_util.h\"", file=fd)
    print("#include \"ldp_dynamic_trigger.h\"", file=fd)
    print("#include \"ldp_network.h\"\n", file=fd)
    print("#include \"route.h\"", file=fd)
    if component_impl.has_cpp_module():
        print("#include \"component_" + component_impl.get_name() + ".hpp\"", file=fd)
    else:
        print("#include \"component_" + component_impl.get_name() + ".h\"", file=fd)
    print("#include \"" + component_impl.get_name() + "_External_Interface.h\"\n\n", file=fd)

    text = ""
    externals_done = []
    for link in component_impl.get_links():
        if link.is_external_c() and link.source_operation not in externals_done:
            if component_impl.is_module_instance(link.target):
                mt = component_impl.find_module_type(link.target)
                op = mt.get_operation(link.target_operation)
            elif component_impl.is_dynamic_trigger_instance(link.target):
                op = component_impl.get_instance(link.target).event_in

            # From ECOA specifications: Due to the chosen approach, only one single instance of
            # one given driver  component implementation can be  deployed  per  protection
            # domain;  this  limitation  does  not preclude  the  deployment  of  several  driver
            # component  instances  within  the  same protection  domain  if they  refer  to
            # distinct  driver  component implementations.
            comp = components[0]

            prototype = generate_external_prototype(component_impl, link)
            text += prototype + "\n{\n"
            text += "    int param_size = 0"
            for param in op.params:
                text += "+sizeof(" + fix_C_data_type(param.type) + ")"
            text += ";\n"

            text_mods = ""
            text_ids = ""
            text_indexes = ""
            text_activating = ""

            text_mod_operations = ""
            n_mods = 0
            for l in component_impl.get_links():
                if l.source_operation == link.source_operation and l.is_external_c():
                    mod_inst = component_impl.get_instance(l.target)

                    # find deployed module
                    dep_mod = None
                    for pd in protection_domains.values():
                        dep_mod = pd.find_deployed_module(l.target, comp.name)
                        if dep_mod is not None:
                            break
                    if dep_mod is None:
                        error("Module not deployed :"+comp.name+" "+ l.target)
                        assert(0)

                    #
                    text_mod_operations += "      {\n"
                    if component_impl.is_dynamic_trigger_instance(l.target):
                        text_mod_operations +=   "        (ldp_module_context*) &" + comp.name \
                                     + "_ctx->dyn_trigger_context[" + str(dep_mod.index) + "],\n"
                    else:
                        text_mod_operations += "        &" + comp.name + "_ctx->worker_context[" + str(
                            dep_mod.index) + "],\n"

                    text_mod_operations += "        " + l.get_op_id() + ",\n"
                    text_mod_operations += "        " + str(mod_inst.entry_links_index[l.target_operation][0]) + ",\n"
                    text_mod_operations += "        " + str(l.activating_op).lower()  + "\n"
                    text_mod_operations += "      },\n"
                    n_mods += 1

            text += "    ldp_mod_operation mod_ops[" + str(n_mods) + "] = {\n"
            text += text_mod_operations
            text += "    };\n"

            text += "    ldp_mod_operation_map operation_map = {\n"
            text += "     .op_name = \"" + link.source_operation + "\",\n"
            text += "     .nb_module = " + str(n_mods) + ",\n"
            text += "     .nb_local_socket = 0,\n"
            text += "     .nb_ext_socket = 0,\n"
            text += "     .module_operations = &mod_ops[0],\n"
            text += "    };\n\n"

            text += "    apr_thread_mutex_lock("+ comp.name + "_ctx->external_mutex);\n"
            text += "\n"
            text += "    char* param_msg = "+ comp.name + "_ctx->external_msg_buffer;\n"
            text += generate_memcpy_parameters(op, "LDP_HEADER_TCP_SIZE", with_input=True)
            text += "    ldp_mod_event_send_local(mod_ops[0].mod_ctx, param_msg, param_size, " \
                    "operation_map, true);\n"
            text += "\n"
            text += "    apr_thread_mutex_unlock("+ comp.name + "_ctx->external_mutex);\n"

            text += "}\n\n"

            # Don't process this external operation again
            externals_done.append(link.source_operation)

    print(text, file=fd)

    fd.close()


def generate_external_prototype(component_impl, link):
    """@TODO Function docstring"""
    if component_impl.is_module_instance(link.target):
        mt = component_impl.find_module_type(link.target)
        op = mt.get_operation(link.target_operation)
    elif component_impl.is_dynamic_trigger_instance(link.target):
        op = component_impl.get_instance(link.target).event_in

    s_params = generate_header_fct(op, with_input=True)
    if not len(s_params):
        s_params = "void"
    else:
        # No context, first comma is not needed
        s_params = s_params[2:]

    return "void " + component_impl.get_name() + "__" + link.source_operation + "(" + s_params + ")"
