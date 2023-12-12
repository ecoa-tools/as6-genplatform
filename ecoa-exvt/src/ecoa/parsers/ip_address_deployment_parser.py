# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

import copy
import os
from xml.etree.ElementTree import ElementTree

from ..models.ip_address_deployment import IP_Address_Deployment, IP_PD_Deployment, IP_Deployed_Module
from ..utilities.logs import info, warning
from ..utilities.xml_utils import validate_XML_file


def parse_ip_address_deployment(integration_directory, xsd_directory):
    filename = os.path.join(integration_directory, "ip_address_deployment.xml")
    if not os.path.exists(filename):
        return None

    info(" == Parse IP deployment files")
    if validate_XML_file(filename, os.path.join(xsd_directory, "ip-address-deployment.xsd")) == -1:
        return None

    tree = ElementTree()
    tree.parse(filename)

    ip_address_deployment = IP_Address_Deployment()
    # protection domain
    for pd in tree.iterfind("protectionDomain"):
        pd_name = pd.get("name")
        for e in pd.iterfind("executeOn"):
            platform_name = e.get("computingPlatform")
            node_name = e.get("computingNode")
            ip_address = e.get("ipAddress", "0.0.0.0")
            ip_address_to_main_process = e.get("ipAddressToMainProcess", "0.0.0.0")
            new_pd = IP_PD_Deployment(pd_name, node_name, platform_name, ip_address, ip_address_to_main_process)

        ## module
        for module in pd.iterfind("deployedModuleInstance"):
            mod_name = module.get("moduleInstanceName")
            comp_name = module.get("componentName")
            new_mod = IP_Deployed_Module(mod_name, comp_name)
            new_pd.add_deployed_module(copy.copy(new_mod))

        ## trigger
        for module in pd.iterfind("deployedTriggerInstance"):
            mod_name2 = module.get("triggerInstanceName")
            comp_name2 = module.get("componentName")
            new_mod = IP_Deployed_Module(mod_name2, comp_name2)
            new_pd.add_deployed_module(copy.copy(new_mod))
        ip_address_deployment.add_protection_domain(copy.copy(new_pd), pd_name)

    return ip_address_deployment


def check_ip_deployment(ip_deployment, protection_domains):
    """Check logic of the ip deployment file

     - dectect if deployed module exists

    Args:
        ip_deployment  (ip_deployment): The ip deployment
        protection_domains     (dict): The dictionary of protection domains

    @return     True or False
    """
    if ip_deployment is None:
        return True

    correct_file = True
    for pd in protection_domains.values():
        # detect if every protection domains have ip deployment property
        if pd.name not in ip_deployment.protection_domain_deployment:
            warning("Protection domain '" + pd.name + "' doesn't have ip deployment properties")
            # correct_file = False

    for pdd in ip_deployment.protection_domain_deployment.values():
        protect_domain = protection_domains[pdd.name]
        for dep_mod in pdd.deployed_modules:
            # detect if every deployed module in ip deployment exists
            if not protect_domain.is_deployed_module(dep_mod.component_name, dep_mod.name):
                warning(
                    "[ip dep] module '" + dep_mod.name + "'' of component '" + dep_mod.component_name + "' is not deployed in protection domain '" + pdd.name + "'")
                correct_file = False

    return correct_file
