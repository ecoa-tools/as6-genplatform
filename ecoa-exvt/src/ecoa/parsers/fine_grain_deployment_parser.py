# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

import os, copy
from xml.etree.ElementTree import ElementTree
from ..models.fine_grain_deployment import Fine_Grain_Deployment, Deployed_Module_Affinity, PD_Deployment
from ..utilities.logs import info, warning
from ..utilities.xml_utils import validate_XML_file


def parse_fine_grain_deployment(integration_directory, xsd_directory):
    filename = os.path.join(integration_directory, "fine_grain_deployment.xml")
    if not os.path.exists(filename):
        return None

    info(" == Parse fine_grain deployment files")
    if validate_XML_file(filename, os.path.join(xsd_directory,"ldp-fine-grain-deployment.xsd")) == -1:
        return None

    tree = ElementTree()
    tree.parse(filename)
    fine_grain_deployement=Fine_Grain_Deployment()

    # platform deployment
    ptd =  tree.find("platformTechnicalDeployment")
    for technical_core in ptd.iterfind("technicalProcessingResource"):
        computing_node = technical_core.get("computingNode")
        computing_platform = technical_core.get("computingPlatform")
        core_id = technical_core.get("coreId")

        fine_grain_deployement.add_technical_core(computing_node, computing_platform, core_id)

    # protection domain
    for pd in tree.iterfind("protectionDomainDeployment"):
        mapping = pd.find("mapping")
        pd_name = mapping.get("protectionDomainName")
        node_name = mapping.get("computingNode")
        platform_name = mapping.get("computingPlatform")
        sched_policy = pd.find("schedulingPolicy").text
        new_pd = PD_Deployment(pd_name, node_name, platform_name, sched_policy)

        # default affinity
        for core in pd.find("defaultAffinity").iterfind("core"):
            new_pd.add_default_core(core.get("id"))

        affinity = pd.find("affinity")
        ## module
        for module in affinity.iterfind("deployedModuleInstance"):
            mod_name = module.get("moduleInstanceName")
            comp_name = module.get("componentName")
            new_mod = Deployed_Module_Affinity(mod_name, comp_name)
            for core in module.iterfind("core"):
                new_mod.add_core(core.get("id"))
            new_pd.add_deployed_module_affinity(copy.copy(new_mod))

        ## trigger
        for module in affinity.iterfind("deployedTriggerInstance"):
            mod_name2 = module.get("triggerInstanceName")
            comp_name2 = module.get("componentName")
            new_mod = Deployed_Module_Affinity(mod_name2, comp_name2)
            for core in module.iterfind("core"):
                new_mod.add_core(core.get("id"))
            new_pd.add_deployed_module_affinity(copy.copy(new_mod))
        fine_grain_deployement.add_protection_domain(copy.copy(new_pd), pd_name)

    return fine_grain_deployement


def check_file_grain_deployment(fine_grain_deployment, protection_domains):
    """Check logic of the fine grain deployment file

    Check if:
        - protection domain are deployment with fine grain properties
        - dectect if deployed module exists

    Args:
        fine_grain_deployment  (fine_grain_deployement): The fine grain deployment
        protection_domains     (dict): The dictionary of protection domains

    @return     True or False
    """
    if fine_grain_deployment == None:
        return True

    correct_file = True
    for pd in protection_domains.values():
        # detect if every protection domains have fine grain deployment property
        if pd.name not in fine_grain_deployment.protection_domain_deployment:
            warning("Protection domain '"+pd.name+"' doesn't have fine grain deployment properties")
            # correct_file = False

        #TODO check mapping
        #TODO check default core ID


    #TODO check mapping aand core ID for technical ressources

    for pdd in fine_grain_deployment.protection_domain_deployment.values():
        protect_domain = protection_domains[pdd.name]
        for dep_mod in pdd.deployed_modules_affinity:
            # detect if every deployed module in fine grain deployment exists
            if not protect_domain.is_deployed_module(dep_mod.component_name, dep_mod.name):
                warning("[fine grain dep] module '"+dep_mod.name+"'' of component '"+dep_mod.component_name+"' is not deployed in protection domain '"+pdd.name+"'")
                correct_file = False

            #TODO Check core ID of module



    return correct_file



