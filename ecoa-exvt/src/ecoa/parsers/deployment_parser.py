# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

import os
from collections import OrderedDict
from xml.etree.ElementTree import ElementTree
from ..models.protection_domain import Protection_Domain
from ..models.platform_configuration import Platform_Configuration
from ..models.wire import Wire
from ..models.deployment import Deployment
from ..utilities.namespaces import ECOS_DE
from ..utilities.logs import error, warning
from ..utilities.xml_utils import validate_XML_file
from ..models.module_instance import Module_Instance


def parse_deployment_files(xsd_directory, deployment_files, assembly_composite, logical_system):
    new_deployment = None
    for dep_file in deployment_files:
        new_deployment = parse_deployment(xsd_directory, dep_file, assembly_composite, logical_system)

    return new_deployment

#
# Function: parse_deployment_definition
#
# Parse one given deployment to create a base of protection of protection
# domains
#
# @TODO: Retrieve the attribute 'notificationMaxNumber' to configure the platform instance
#        This obliges to create a new object 'PlatformInstance'
#
def parse_deployment(xsd_directory, filename, assembly_composite, logical_system):

    if os.path.exists(filename) is False:
        error("File '%s' does not exist" % filename)
        return None

    if validate_XML_file(filename, xsd_directory + "/Schemas_ecoa/ecoa-deployment-2.0.xsd") == -1:
        return None

    tree = ElementTree()
    tree.parse(filename)

    # deployment name
    deployment_name = os.path.basename(filename)
    if deployment_name.endswith(".deployment.xml"):
        # normal case. filename = #name#.deployment.xml
        deployment_name= deployment_name.replace(".deployment.xml", "")
    else:
        # support non-compliant filename
        warning("Deployment file '%s' isn't a compliant filename. Should be '#name#.deployment.xml'" % os.path.basename(filename))
        deployment_name = deployment_name.replace(".xml", "")

    # Assembly
    final_assembly_name = tree.getroot().get("finalAssembly")
    if final_assembly_name != assembly_composite.name:
        error("In deployment files '%s', final assembly '%s' is not defined" % (filename, final_assembly_name))
        components = OrderedDict()
    else:
        components = assembly_composite.components

    # logical system
    logical_system_name = tree.getroot().get("logicalSystem")
    if logical_system_name != logical_system.name:
        error("In deployment files '%s', logical system '%s' is not defined" % (filename, logical_system_name))
        platforms = OrderedDict()
    else:
        platforms = logical_system.platforms

    new_deployment = Deployment(deployment_name, final_assembly_name, logical_system_name)

    l_nodes_list = set()
    # protection domains
    for pd in tree.iterfind(ECOS_DE + "protectionDomain"):
        name_pd = pd.get("name")

        for e in pd.iterfind(ECOS_DE + "executeOn"):
            platform = e.get("computingPlatform")
            node = e.get("computingNode")
            l_nodes_list.add(node)

        protection_domain = Protection_Domain(name_pd, platform, node,
                                              final_assembly_name, logical_system_name)

        for m in pd.iterfind(ECOS_DE + "deployedModuleInstance"):
            cn = m.get("componentName")
            mn = m.get("moduleInstanceName")
            mp = m.get("modulePriority")
            protection_domain.add_module(mn, cn, "module")
            if cn not in components:
                error("In deployment file , component name " + cn + " doesn't exist")
                continue

            comp = components[cn]
            comp.mod_set_protection_domain(mn, name_pd)
            comp.mod_set_node(mn, node)
            comp.mod_set_priority(mn, int(mp))

        for t in pd.iterfind(ECOS_DE + "deployedTriggerInstance"):
            cn = t.get("componentName")
            tn = t.get("triggerInstanceName")
            tp = t.get("triggerPriority")
            protection_domain.add_module(tn, cn, "trigger")
            if cn not in components:
                error("Component name " + cn + " doesn't exist")
                continue

            comp = components[cn]
            comp.mod_set_protection_domain(tn, name_pd)
            comp.mod_set_node(tn, node)
            comp.mod_set_priority(tn, int(tp))

        #new_deployment.protection_domains[protection_domain.name] = protection_domain
        new_deployment.add_protection_domain(protection_domain)

    # Activate multi-node mode when deployment is dispatched on multiple nodes
    new_deployment.multi_node = len(l_nodes_list) > 1

    ## PF configuration
    for pf in tree.iterfind(ECOS_DE + "platformConfiguration"):
        computing_pf = pf.get("computingPlatform")
        max_nb_notification = int(pf.get("faultHandlerNotificationMaxNumber"))
        # new_deployment.platform_configurations[computing_pf] =
        new_deployment.add_platform_config(computing_pf,
                                            Platform_Configuration(computing_pf, max_nb_notification))

        for pf_node_config in pf.iterfind(ECOS_DE + "computingNodeConfiguration"):
            node_ID = pf_node_config.get("computingNode")
            new_deployment.add_platform_config_node(computing_pf, node_ID)
            # TODO add schedulingInformation

    ## Wires mapping
    for wire_map in tree.iterfind(ECOS_DE + "wireMapping"):
        pf_link_id = wire_map.get("mappedOnLinkId")
        (source_comp, source_serv) = wire_map.get("source").split('/')
        (target_comp, target_serv) = wire_map.get("target").split('/')

        new_deployment.add_wire_mapping(pf_link_id, Wire(source_comp, source_serv, target_comp, target_serv))
        # if pf_link_id not in wireMapping:
        #     wireMapping[pf_link_id]=[]
        # new_deployment.wireMapping[pf_link_id].append(Wire(source_comp, source_serv, target_comp, target_serv))


    # Log policy
    for l in tree.iterfind(ECOS_DE + "logPolicy"):
        for c in l.iterfind(ECOS_DE + "componentLog"):
            comp_name = c.get("instanceName")
            log_levels = c.get("enabledLevels").replace(" ", "")
            if comp_name not in components:
                error("logpolicy in deployment file : Component name '" + comp_name + "' doesn't exist")
            else:
                comp = components[comp_name]
                comp.set_log_policy(log_levels)
                for m in c.iterfind(ECOS_DE + "moduleLog"):
                    mod_name = m.get("instanceName")
                    mod_log_levels = m.get("enabledLevels").replace(" ", "")
                    comp.mod_set_log_policy(mod_name, mod_log_levels)

    return new_deployment


##
## Check if ????
##
## components and components implementations are supposed correct
def check_deployment(deployment, final_assembly_composite, component_implementations, logical_system):
    components = final_assembly_composite.components
    platforms = logical_system.platforms

    ret_val = True
    for pd in deployment.protection_domains.values():
        # check platform
        if pd.platform not in platforms:
            warning("deployment, protection domain '%s' is deployed on an unknown platform '%s'" %
                    (pd.name, pd.platform))

        # check if depoyed module exists in component
        for mod_deployed in pd.deployed_modules:
            # check if component exists
            if mod_deployed.component_name not in components:
                error("deployment, component " + mod_deployed.component_name + " does not exist")
                ret_val = False
            else:
                comp_impl_name = components[mod_deployed.component_name].component_implementation
                if comp_impl_name not in component_implementations:
                    error("deployment, component implementation " + comp_impl_name + " does not exist")
                    ret_val = False
                    continue

                # check if module exist in component
                comp_impl, _ = component_implementations[comp_impl_name]
                if mod_deployed.name not in [m.name for m in comp_impl.module_instances] \
                                          + [m.name for m in comp_impl.trigger_instances] \
                                          + [m.name for m in comp_impl.dynamic_trigger_instances]:
                    error("deployment, " + mod_deployed.name
                        + " does not exist in component " + mod_deployed.component_name)
                else:
                    # check if module type are deployed with the same type
                    mod_inst = comp_impl.get_instance(mod_deployed.name)
                    if (isinstance(mod_inst, Module_Instance) and mod_deployed.type != 'module') or \
                       (not isinstance(mod_inst, Module_Instance) and mod_deployed.type != 'trigger'):
                        error("Deployed module '%s' in component '%s' is deployed as a %s" \
                            % (mod_deployed.name, mod_deployed.component_name,mod_deployed.type))
                        ret_val = False
        if ret_val:
            ret_val = pd.check_protection_domain(components, component_implementations)

    # check if every components and modules are deployed in a protection domain
    for comp in components.values():
        if comp.component_implementation == "":
            # component without a component implementation (define in an other Platform)
            continue
        comp_impl,_ = component_implementations[comp.component_implementation]
        for mod in comp_impl.module_instances+comp_impl.trigger_instances+comp_impl.dynamic_trigger_instances:
            mod_defined = False
            for pd in deployment.protection_domains.values():
                if(pd.is_deployed_module(comp.name, mod.name)):
                    mod_defined = True
                    break
            if not mod_defined:
                error("module '%s' in component '%s' is not deployed"%(mod.name, comp.name))

        # check log policy of module
        for mod_name in comp.mod_log_levels.keys():
            if comp_impl.get_instance(mod_name) == None:
                warning(("In component '%s', logpolicy is setted to an unknown module"+
                      " instance '%s' in component implementation '%s' ") %
                        (comp.name, mod_name, comp_impl.name))

    return ret_val

def check_wire_mapping(wire_mapping, platform_links, wires):
    # PF_links exist
    # wires exist

    succes=True
    for pf_link_id, wires_mapped in wire_mapping.items():
        # Check pf link id
        if pf_link_id not in platform_links:
            error("Wire is mapped on an invalid PF link '%s'" %(pf_link_id))
            succes=False

        # check wires
        for w in wires_mapped:
            if w not in list(wires):
                error("Wire '%s' is mapped but it doesn't exit. " %(str(w)))
                succes=False

    return succes
