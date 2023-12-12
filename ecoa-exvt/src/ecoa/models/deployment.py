# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

from collections import OrderedDict

class Deployment:
    """Description of a deployment

    Attributes:
        name                (str): name of the deployment (xxx.deployment.xml)
        assembly_name       (str): name of the deployed assembly
        logical_sys_name    (str): name of the logical system onto the assembly
                                   is deployed
        protection_domains (dict): Deployed protection domain.
                                   Dictionary of :class:`Protection_Domain`

        wire_mapping       (dict): mapping of wires on Platform Links.
                                   Dictionary of :class:`wires` retrieved by
                                   Platform link ID.
        platforms_config   (dict): configuration of Platform.
                                   Dictionary of :class:`Platform_Configuration`
                                   retrieved by Platform name.
    """
    def __init__(self, name, assembly_name, logical_sys_name):
        self.name = name
        self.assembly_name = assembly_name
        self.logical_sys_name = logical_sys_name

        self.protection_domains = OrderedDict()
        self.wire_mapping = OrderedDict()
        self.platforms_config = OrderedDict() #PF_name -> Platform configuration
        self.multi_node = False

    def add_wire_mapping(self, pf_link_id, wire):
        self.wire_mapping.setdefault(pf_link_id, [])
        self.wire_mapping[pf_link_id].append(wire)

    def add_platform_config(self, PF_name, PF_config):
        self.platforms_config[PF_name] = PF_config

    def add_platform_config_node(self, PF_name, node_ID):
        self.platforms_config[PF_name].add_computing_node(node_ID)

    def add_protection_domain(self, new_protection_domain):
        self.protection_domains[new_protection_domain.name] = new_protection_domain
