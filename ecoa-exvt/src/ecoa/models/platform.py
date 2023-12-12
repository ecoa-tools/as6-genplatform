# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

from ..utilities.logs import error, warning
from collections import OrderedDict

class Platform:
    """Describes an instance of platform used within an assembly schema

    Attributes:
        id     (int) : unique number
        name   (str) : platform name. Processor identifier
        nodes  (dict): dictionary of :class:`.Node` with in the platform (retrieved by node name)
        links  (set) : NO USED
    """
    id_counter = 0

    def __init__(self, name, ELI_ID):
        self.name = name
        self.id = Platform.id_counter
        self.nodes = OrderedDict()
        self.node_links = set() ## TODO: use dictionary with link IDs as keys ?
        self.platform_message_link = "" #: platform link ID to send ELI platform messages

        if ELI_ID != "":
            self.ELI_platform_ID = int(ELI_ID)
        else:
            warning("ELIPlatformId is not defined for '%s'. Unicity of ELIPlatformId cannot be assured" % (name))
            self.ELI_platform_ID = Platform.id_counter

        Platform.id_counter = Platform.id_counter + 1

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def add_logical_node(self, node):
        if node.name in self.nodes:
            error("The node %s is declared two types in platform %s" % (node.name, self.name))
        self.nodes[node.name] = node
        return True

    def add_node_link(self, node_link):
        self.node_links.add(node_link)

    def get_processors_number(self):
        nb = 0
        for lnid, ln in self.nodes.items():
            nb = nb + ln.get_processors_number()
        return nb

    def get_mean_step_duration(self):
        mean = 0
        nb = 0
        for lnid, ln in self.nodes.items():
            mean = mean + ln.get_mean_step_duration() * ln.get_processors_number()
            nb = nb + ln.get_processors_number()
        if nb != 0:
            mean = mean / nb
        else:
            mean = -1
        return int(mean)

    def get_mean_module_switch_time(self):
        mean = 0
        for lnid, ln in self.nodes.items():
            mean = mean + ln.get_module_switch_time()
        if len(self.nodes) != 0:
            mean = mean / len(self.nodes)
        else:
            mean = -1
        return int(mean)

    def set_composite_name(self, composite_name):
        self.composite_name = composite_name

    def set_composite_impl_name(self, upper_composite):
        self.composite_impl_name = upper_composite.get_component_impl(self.composite_name)

    def find_PF_composite_type(self, cross_PF_view, upper_composite, platform_composites):
        """Find the composite type (defined in initial assembly) of the platform

        Arguments:
            cross_PF_view       (:class:`.cross_platform_view`): The cross pf view
            upper_composite     (:class:`.Composite`)          : The upper composite
            platform_composites (dict): The platform composites. dictionay of :class:`.Composite`

        Return:
            (:class:`.Composite`) : composite type defined in the InitialAssembly, or None
        """

        pf_composite = cross_PF_view.find_composite_name(self.name)
        if pf_composite != "" and  pf_composite in upper_composite.components:
            pf_composite_type_name = upper_composite.components[pf_composite].composite_name
            if pf_composite_type_name in platform_composites:
                return platform_composites[pf_composite_type_name]
        return None
