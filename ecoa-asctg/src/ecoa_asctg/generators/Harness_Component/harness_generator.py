# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

from ecoa.utilities.logs import info, debug
from collections import OrderedDict

from ecoa.models.wire import Wire

from .harness_utils import get_harness_type_str, get_harness_str, write_xml_file
from .harness_impl_generator import harness_generate_comp_impl
from .harness_type_generator import harness_generate_component_type
from .harness_deployment_generator import update_deployment_file
from .harness_composite_generator import update_composite_file
from .harness_project_generator import update_project_config_file


def __harness_find_new_wires(harness_comp_name, component_types, components, wires, harness_comps):
    """Find new wires which must be connected with harness component

    Attributes:
        harness_comp_name  (str):The harness component name
        component_types   (dict):The dictionary of :class:`~ecoa.models.component_type.Component_Type`
        components        (dict):The dictionary of :class:`~ecoa.models.component.Component`
        wires             (dict):The dictionary of existing :class:`~ecoa.models.wire.Wire`
        harness_comps     (list):The list of componenents handled by harness

    Return:
        tuple(list, list) : list of wires to keep and list of new wires :class:`~ecoa.models.wire.Wire`
    """
    keep_wires = []
    new_wires = []
    info("Harness for component(s) '%s'" % ', '.join(harness_comps))
    debug("Wires :%s" % wires)
    for c_wire in wires:
        l_source_comp_in_harness_comps = c_wire.get_source_component() in harness_comps
        l_target_comp_in_harness_comps = c_wire.get_target_component() in harness_comps
        # Two components are in the HARNESS components list (we keep the wire between them)
        if l_source_comp_in_harness_comps and l_target_comp_in_harness_comps:
            keep_wires.append(c_wire)
        # The source component is only in the HARNESS components list (add wire from soure component to HARNESS)
        elif l_source_comp_in_harness_comps and not l_target_comp_in_harness_comps:
            new_wires.append(Wire(c_wire.get_source_component(), c_wire.get_source_service(),
                                  harness_comp_name, c_wire.get_source_component() + "_" + c_wire.get_source_service()))
        # The target component is only in the HARNESS components list (add wire from HARNESS to target component)
        elif not l_source_comp_in_harness_comps and l_target_comp_in_harness_comps:
            new_wires.append(Wire(harness_comp_name, c_wire.get_target_component() + "_" + c_wire.get_target_service(),
                             c_wire.get_target_component(), c_wire.get_target_service()))

    debug("Harness old wires :%s" % keep_wires)
    debug("Harness new wires :%s" % new_wires)

    return keep_wires, new_wires


def __harness_find_ref_svc(harness_comp_name, keep_wires, new_wires, component_types, components, service_definitions):
    """Find harness services and references. Find also syntax and corresponding wire

    Attributes:
        harness_comp_name    (str):The harness component name
        new_wires           (list):The new wires
        component_types     (dict):The dictionary of component types
        components          (dict):The dictionary of components. Use to find syntax of service
        service_definitions (dict):The dictionary of service definitions. Use to find syntax of service

    Returns:
        (dict): Dictionary of (service syntax, wire) retrieved by service name. The services of harness component
        (dict): Dictionary of (service syntax, wire) retrieved by service name. The references of harness component
    """
    harness_svc = OrderedDict()  # service name => (service syntax, wire)
    harness_ref = OrderedDict()  # service name => (service syntax, wire)
    for w in new_wires+keep_wires:
        if w.source_component == harness_comp_name:
            other_comp_type, _ = component_types[components[w.target_component].component_type]
            syntax_name = other_comp_type.find_service_syntax(w.target_service)
            harness_ref[w.source_service] = (service_definitions[syntax_name][0], w)

        elif w.target_component == harness_comp_name:
            other_comp_type, _ = component_types[components[w.source_component].component_type]
            syntax_name = other_comp_type.find_service_syntax(w.source_service)
            harness_svc[w.target_service] = (service_definitions[syntax_name][0], w)

    return harness_svc, harness_ref


def __find_harness_modules(services, references):
    """Find harness modules (one per connected component) and wires (with correcponding service syntax)
       that must be connected by a link to the module.

    Attributes:
        services   (dict):The dictionary services of the harness component
        references (dict):The dictionary references of the harness component

    Returns:
        (dict): dictionary of tuple (service syntax, wire) retrieved by module name
    """
    modules_wires_svc = OrderedDict()

    for svc_name, (syntax, wire) in services.items():
        if wire.source_component not in modules_wires_svc:
            modules_wires_svc[wire.source_component] = []
        modules_wires_svc[wire.source_component].append((syntax, wire))

    for svc_name, (syntax, wire) in references.items():
        if wire.target_component not in modules_wires_svc:
            modules_wires_svc[wire.target_component] = []
        modules_wires_svc[wire.target_component].append((syntax, wire))

    return modules_wires_svc


def harness_generate(global_config):
    harness_type_comp_name = get_harness_type_str()
    harness_comp_name = get_harness_str()

    # find wires to connect with an harness component
    keep_wires, new_wires = __harness_find_new_wires(harness_comp_name,
                                         global_config.component_types,
                                         global_config.final_assembly_composite.components,
                                         global_config.final_assembly_composite.wires,
                                         global_config.harness_components)

    if not new_wires:
        info("No unconnected services has been found. Nothing to generate.")
        return

    # find servcies and references
    new_services, new_references = __harness_find_ref_svc(harness_comp_name,
                                                          keep_wires,
                                                          new_wires,
                                                          global_config.component_types,
                                                          global_config.final_assembly_composite.components,
                                                          global_config.service_definitions)

    # find harness modules and connected wires
    modules_wires_svc = __find_harness_modules(new_services, new_references)

    # component type:
    root_comp_type = harness_generate_component_type(new_services, new_references)
    harness_comp_type_file = global_config.m_harness_comp_type_file
    write_xml_file(global_config, global_config.m_harness_comp_type_file, root_comp_type)
    info("Component type file '%s' has been created" % global_config.m_harness_comp_type_file)

    # component implementation:
    root_comp_impl = harness_generate_comp_impl(global_config.libraries, modules_wires_svc,
                                                new_services, new_references)
    write_xml_file(global_config, global_config.m_harness_comp_impl_file, root_comp_impl)
    info("Component implementation file '%s' has been created" % global_config.m_harness_comp_impl_file)

    # update .project.xml
    update_project_config_file(global_config,
                                 global_config.platform_config_file)

    # Update composite file
    update_composite_file(global_config,
                            harness_type_comp_name,
                            harness_comp_name,
                            global_config.harness_components,
                            keep_wires,
                            new_wires,
                            new_services,
                            new_references,
                            global_config.m_composite_filename)

    # update deployment file
    # find a platform and a node to deloyed harness modules
    computing_PF_name = "Ldp"
    computing_node_name = "machine0"
    if len(global_config.logical_system.platforms) > 0:
        arbitrary_plaform = list(global_config.logical_system.platforms.values())[0]
        computing_PF_name = arbitrary_plaform.name
        if len(arbitrary_plaform.nodes) > 0:
            computing_node_name = list(arbitrary_plaform.nodes.keys())[0]

    update_deployment_file(global_config,
                             harness_comp_name,
                             global_config.harness_components,
                             global_config.m_deployment_filename,
                             computing_PF_name,
                             computing_node_name)
