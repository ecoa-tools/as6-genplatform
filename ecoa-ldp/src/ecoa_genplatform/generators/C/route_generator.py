# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

import os
from collections import OrderedDict
from ecoa.utilities.logs import debug, error, warning
from ..version_header_generator import generate_ldp_version_header_warning
from ecoa.models.wire import Wire
from ecoa.models.module_instance import Module_Instance
from ecoa.utilities.euid_generator import _generate_ID_value
from ecoa.utilities.euid_generator import generate_IDs
from ..fix_names import fix_C_data_type
from ..force_generation import file_need_generation

def generate_params_size(params):
    l_size = "0"
    for param in params:
        l_size += "+sizeof(" + fix_C_data_type(param.type) + ")"
    return l_size

def get_node_from_wire(protection_domains, wire):
        for pd in protection_domains.keys():
            for mod in protection_domains[pd].deployed_modules:
                if wire.get_target_component() == mod.component_name:
                    return protection_domains[pd].node
        return None

def generate_route(multi_node, route, output_directory, force_flag, instance_index, protection_domains, components,
                   PF_links, current_platform, platforms,
                   integration_directory, project_name, nodes_deployment=None):
    """@TODO Function docstring"""
    c_filename = os.path.join(output_directory, 'route.h')

    if not file_need_generation(c_filename,
                            force_flag,
                            "    route.h already exists"):
        return

    fd = open(c_filename, 'w')
    text = generate_ldp_version_header_warning() + \
           "#ifndef _ROUTE_H \n\
#define _ROUTE_H \n\
\n\
#define ID_INITIALIZE_event \"INITIALIZE\" \n\
#define ID_START_event \"START\" \n\
#define ID_STOP_event \"STOP\" \n\
#define MODULE_BASE_PORT (20000+" + str(instance_index * 1000) + ")\n\
#define COMPONENT_BASE_PORT (MODULE_BASE_PORT + 10000)\n"
    print(text, file=fd)

    text = "// ELI Platform IDs\n"
    for pf in platforms.values():
        text += "#define ELI_PF_" + pf.name + " (" + str(pf.ELI_platform_ID) + ")\n"
    print(text, file=fd)

    text = "// Platform links\n"
    for pf_l in PF_links.values():
        if current_platform.name == pf_l.source_platform:
            other_PF_name = pf_l.target_platform
        else:
            other_PF_name = pf_l.source_platform
        text += "#define " + pf_l.name + "_read_port (" + pf_l.link_binding.find_read_mcast_port(
            current_platform.name) + ")\n"
        text += "#define " + pf_l.name + "_read_addr \"" + pf_l.link_binding.find_read_mcast_address(
            current_platform.name) + "\"\n"
        text += "#define " + pf_l.name + "_sent_port (" + pf_l.link_binding.find_read_mcast_port(other_PF_name) + ")\n"
        text += "#define " + pf_l.name + "_sent_addr \"" + pf_l.link_binding.find_read_mcast_address(
            other_PF_name) + "\"\n"
        text += "#define " + pf_l.name + "_sent_PF_ID (" + pf_l.link_binding.find_mcast_PF_id(
            current_platform.name) + ")\n"
        text += "#define " + pf_l.name + "_read_PF_ID (" + pf_l.link_binding.find_mcast_PF_id(other_PF_name) + ")\n"

    print(text, file=fd)

    # macro for father-component connections
    pd_index = 0
    text = "// local-node IP connections with master process\n"
    for pd_name in protection_domains.keys():
        ip_addr = "0.0.0.0"
        if multi_node:
            # In this case we are on multi nodes
            if nodes_deployment is None:
                error("[Main Process] missing nodes_deployment.xml file mandatory with multi nodes")
            else:
                ip_addr = nodes_deployment["main"]

        text += "#define " + pd_name + "_addr \"" + ip_addr + "\" \n"
        text += "#define " + pd_name + "_port (COMPONENT_BASE_PORT+" + str(pd_index) + ") \n\n"
        pd_index += 1
    print(text, file=fd)

    # module tcp connections
    text = "// local-node IP connections between PD\n"
    for wire in route.wires:
        if wire.is_map_on_PF_link():
            pass
        else:
            ip_addr = "0.0.0.0"
            if multi_node:
                # In this case we are on multi nodes
                if nodes_deployment is None:
                    error("[PD] missing nodes_deployment.xml file mandatory with multi nodes")
                else:
                    l_node = get_node_from_wire(protection_domains, wire)
                    ip_addr = nodes_deployment[l_node]

            text += "#define " + wire.name() + "_port (MODULE_BASE_PORT+" + str(wire.id) + ")\n"
            text += "#define " + wire.name() + "_addr \"" + ip_addr + "\"\n"
    print(text, file=fd)

    # wire service IDs
    text = "\n// wire service IDs\n\n"
    for w in route.wires:
        comp_type_name = route.components[w.source_component].component_type
        if comp_type_name not in route.component_types:
            comp_type_name = route.components[w.target_component].component_type
        if comp_type_name not in route.component_types:
            error("invalid wire : cannot find EUIDs for wire '%s'" % (w))
            continue

        serv_syntax_name = route.component_types[comp_type_name][0].find_service_syntax(w.source_service)
        for op in route.service_definitions[serv_syntax_name][0].operations:
            macro_name = repr(w) + ":" + op.name
            l_serviceId = str(route.IDs[macro_name]).replace(":", "__").replace("/", "_")
            text += "#define " + w.name() + "__" + op.name + " " + l_serviceId + "\n"

    print(text, file=fd)

    # module op IDs
    text = "\n// module op ID\n\n"
    new_op_id = 200
    for pd in protection_domains.values():
        text += " /// " + pd.name + "\n"
        for dep_mod in sorted(list(pd.deployed_modules)):
            comp = route.components[dep_mod.component_name]
            comp_type, _ = route.component_types[comp.component_type]
            comp_impl, _ = route.component_implementations[comp.component_implementation]
            m_inst = comp_impl.get_instance(dep_mod.name)

            if comp_impl.is_dynamic_trigger_instance(dep_mod.name):
                text += "#define " + dep_mod.component_name + "__" + dep_mod.name \
                        + "__in ID_dynamic_trigger_in\n"
                text += "#define " + dep_mod.component_name + "__" + dep_mod.name \
                        + "__reset ID_dynamic_trigger_reset\n"
                for op_name, link_list in list(m_inst.entry_points_dict.items()):
                    for l in [l for l in link_list if l.is_external()]:
                        text += "#define ID_External_" + dep_mod.name + "_" + op_name \
                                + " ID_dynamic_trigger_in // extrenal\n"  # external
                        new_op_id += 1
                        break
            else:
                macro_name_dict = set()
                text += "// " + dep_mod.name + " " + dep_mod.component_name + "\n"
                for op_name, link_list in list(m_inst.entry_points_dict.items()) \
                                          + list(m_inst.out_points_dict.items()):
                    macro_name = dep_mod.component_name + "__" + dep_mod.name + "__" \
                                 + op_name.replace('.', '_').replace("e-", "E_")

                    if macro_name not in macro_name_dict:
                        macro_name_dict.add(macro_name)
                        if len(link_list) > 0 and link_list[0].type != "RR":
                            # normal case
                            if link_list[0].type == "data":
                                l_RR_id = str(new_op_id)
                                new_op_id += 1
                            else:
                                l_wire = link_list[0].find_connected_wires_link(dep_mod.component_name, route.wires)
                                l_pd_components = pd.get_all_component_names()
                                if len(l_wire) > 0 and (l_wire[0].source_component in l_pd_components and l_wire[0].target_component in l_pd_components):
                                    if comp_impl.is_module_instance(link_list[0].target):
                                        l_operation = link_list[0].source_operation
                                    else:
                                        l_operation = link_list[0].target_operation
                                    l_RR_id = l_wire[0].name() + "__" + l_operation
                                else:
                                    l_RR_id = str(new_op_id)
                                    new_op_id += 1
                            text += "#define " + macro_name + " " + l_RR_id + "//\n"


                            if len([l for l in link_list if l.is_external()]) > 0:
                                text += "#define ID_External_" + dep_mod.name + "_" \
                                        + op_name + " " + macro_name + "// external\n"  # external link

                        elif len(link_list) > 0 and link_list[0].type == "RR":
                            # for RR link
                            if link_list[0].target == dep_mod.name:
                                ## for the server module
                                l_wire = link_list[0].find_connected_wires_link(dep_mod.component_name, route.wires)
                                l_pd_components = pd.get_all_component_names()
                                if len(l_wire) > 0 and (l_wire[0].source_component in l_pd_components and l_wire[0].target_component in l_pd_components):
                                    if comp_impl.is_module_instance(link_list[0].target):
                                        l_operation = link_list[0].source_operation
                                    else:
                                        l_operation = link_list[0].target_operation
                                    l_RR_id = l_wire[0].name() + "__" + l_operation
                                else:
                                    l_RR_id = str(new_op_id)
                                    new_op_id += 1
                                text += "#define " + macro_name + " " + l_RR_id \
                                        + " //\n"  # RR link
                            else:
                                ## for the client module
                                if len(link_list) != 1:
                                    error("Client connected to multiple server. "
                                          "Invalide RR behaviour")
                                    continue

                                if comp_impl.is_module_instance(link_list[0].target):
                                    # module in the same comp
                                    text += "#define " + macro_name + " " + dep_mod.component_name + "__" \
                                            + link_list[0].target + "__" + link_list[0].target_operation \
                                            + "//\n"
                                else:
                                    # find server module name, server component name,
                                    # server operation name
                                    if len(link_list[0].find_connected_wires_link(comp.name, route.wires)) != 1:
                                        text += "#define " + macro_name + " " + str(
                                            new_op_id) + "// no link in component \n"
                                        new_op_id += 1
                                        warning("No connected wire to link " + str(
                                            link_list[0]) + " in component implementation " + comp_impl.name)
                                        continue

                                    wire = link_list[0].find_connected_wires_link(
                                        comp.name, route.wires)[0]

                                    serv_comp_name = wire.target_component
                                    serv_serv_name = wire.target_service

                                    serv_comp_impl_name = route.components[serv_comp_name].component_implementation

                                    found_link = False
                                    if serv_comp_impl_name != "":
                                        serv_comp_impl, _ = \
                                            route.component_implementations[serv_comp_impl_name]

                                        for l in serv_comp_impl.links:
                                            # find a link in server component to find the server module
                                            if l.source == serv_serv_name \
                                                    and l.source_operation == \
                                                    link_list[0].target_operation:
                                                text += "#define " + macro_name + " " + serv_comp_name \
                                                        + "__" + l.target + "__" + l.target_operation \
                                                        + "//\n"
                                                found_link = True
                                                break
                                    else:
                                        # component not deployed on this PF
                                        pass

                                    if not found_link:
                                        # no link in server component
                                        text += "#define " + macro_name + " " + str(
                                            new_op_id) + "// no link in server component \n"
                                        new_op_id += 1

                        else:
                            text += "#define " + macro_name + " " + str(new_op_id) + "// no link \n"
                            new_op_id += 1
                    else:
                        pass

    print(text, file=fd)

    text = "\n#endif /* _ROUTE_H */"
    print(text, file=fd)
    fd.close()
