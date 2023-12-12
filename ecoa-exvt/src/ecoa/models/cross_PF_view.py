# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

from .wire import Wire
from ..utilities.logs import warning
from collections import OrderedDict

class cross_platforms_view:
    """Cross platform view

    Attributes:
        name                   (str): name of the view
        assembly_name          (str): name of the assembly diagram
        logical_system_name    (str): logical system name
        composites_deployment (dict): deployment composite in platform. composite name => platform name
        euid_binding          (dict): EUID file for a platform link. PF link ID => name of euids file
        cross_PF_wire_mapping (dict): wire mapping of composite wires. PF link ID => logical wires
        EUIDs                 (dict): cross platform IDs for each files. euids file => dict(key, value)

    """
    def __init__(self, name, assembly_name, logical_system_name):
        self.name = name
        self.assembly_name = assembly_name
        self.logical_system_name = logical_system_name
        self.composites_deployment = OrderedDict() # composite name => deployed PF name
        self.euid_binding = OrderedDict() # PF link ID => name of euids file
        self.cross_PF_wire_mapping = OrderedDict() # PF link ID => logical wires
        self.EUIDs = OrderedDict() # euids file => dict(key, value)

    def add_wire_map(self, PF_link_ID, source_comp, source_serv, target_comp, target_serv):
        if PF_link_ID not in self.cross_PF_wire_mapping:
            self.cross_PF_wire_mapping[PF_link_ID]=[]
        self.cross_PF_wire_mapping[PF_link_ID].append(Wire(source_comp, source_serv, target_comp, target_serv))

    def add_euid_binding(self, euids_file, linkID):
        self.euid_binding[linkID] = euids_file

        if euids_file not in self.EUIDs:
            self.EUIDs[euids_file] = OrderedDict()

    def find_composite_name(self, platform_name):
        for comp_name, name in self.composites_deployment.items():
            if name == platform_name:
                return comp_name
        return ""

    def find_missing_EUIDs(self, upper_composite, service_definitions):
        missing_EUIDs = OrderedDict() # binding_file => list of missing EUIDs

        for pf_link_id, wire_list in self.cross_PF_wire_mapping.items():
            binding_file = self.euid_binding[pf_link_id]

            for wire in wire_list:
                syntax_name = upper_composite.get_wire_syntax(wire)
                if syntax_name not in service_definitions:
                    continue
                else:
                    for op in service_definitions[syntax_name][0].operations:
                        wire_id_key = wire.__repr__()+":"+op.name
                        if wire_id_key not in self.EUIDs[binding_file]:
                            missing_EUIDs.setdefault(binding_file,[]).append(wire_id_key)
                            warning("in binding file '%s', missing EUID for '%s'" % (binding_file, wire_id_key))

        return missing_EUIDs
