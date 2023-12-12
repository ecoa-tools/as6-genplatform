# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

from collections import OrderedDict

class IP_Deployed_Module:
    """Describe deployed module

	Attributes:
		name           (str): name of the module
		component name (str): name of the module's component
	"""

    def __init__(self, name, component_name):
        self.name = name
        self.component_name = component_name


class IP_PD_Deployment:
    """Describe deployment properties of Protection Domain:

	Attributes:
		name              (str): name of protection domain
		node_name         (str): name of executing node of protection domain
		platform_name      (str): name of platform of protection domain
		ip_address        (str): ip of the machine where the protection domain is
		deployed_modules (list):list of :class:`.Deployed_Module` to describe deployed modules
	"""

    def __init__(self, name, node_name, platform_name, ip_address, ip_address_main_to_process):
        self.name = name
        self.node_name = node_name
        self.platform_name = platform_name
        self.ip_address = ip_address
        self.ip_address_to_main_process = ip_address_main_to_process
        self.deployed_modules = []

    def add_deployed_module(self, new_module):
        self.deployed_modules.append(new_module)

    def find_module(self, mod_name, comp_name):
        """Find :class:`.Deployed_Module` of deployed module

		Args:
			mod_name  (str): deployed module name
			comp_name (str): component name of module

		return:
			(:class:`.Deployed_Module`): None if deployed module is not found
		"""
        for dep_mod in self.deployed_modules:
            if mod_name == dep_mod.name and comp_name == dep_mod.component_name:
                return dep_mod

        return None


class IP_Address_Deployment:
    """Describe ip deployment of an LDP platform
	"""

    def __init__(self):
        self.protection_domain_deployment = OrderedDict()

    def add_protection_domain(self, protection_domain, name):
        self.protection_domain_deployment[name] = protection_domain

    def get_protection_domain(self, pd_name):
        if pd_name in self.protection_domain_deployment:
            return self.protection_domain_deployment[pd_name]
        else:
            return None

    def get_protection_domain_from_wire(self, wire):
        for pd in self.protection_domain_deployment.keys():
            for mod in self.protection_domain_deployment[pd].deployed_modules:
                if wire.get_target_component() == mod.component_name:
                    return self.protection_domain_deployment[pd]

        return None
