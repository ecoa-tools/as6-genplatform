# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

from collections import OrderedDict


class udp_binding:
    def __init__(self, filename):
        self.filename = filename
        self.platforms = OrderedDict()
        # self.max_channel = 15 # TODO : 256

    def add_platform(self, name, received_mcast_address, received_mcast_port, platform_id, max_channel):
        self.platforms[name] = (received_mcast_address, received_mcast_port, platform_id, max_channel)


    def find_read_mcast_address(self, platform_name):
        if platform_name not in self.platforms:
            return ""
        else:
            return self.platforms[platform_name][0]

    def find_read_mcast_port(self, platform_name):
        if platform_name not in self.platforms:
            return ""
        else:
            return self.platforms[platform_name][1]

    def find_mcast_PF_id(self, platform_name):
        if platform_name not in self.platforms:
            return ""
        else:
            return self.platforms[platform_name][2]

    def find_max_channel(self, platform_name):
        if platform_name not in self.platforms:
            return 15
        else:
            return self.platforms[platform_name][3]

class PlatformLink:
    """Description of platform link

    Attributes:
        source_platform  (str): source platform name
        target_platform  (str): target platform name
        throughput       (str): mega bytes per second
        latency          (str): micro seconds
        id               (str): link ID
        protocol         (str): protocol of communication of this link
        service_syntax  (dict): Wires and corresponding syntax which are
                                mapped on this link.
                                Dictionary of list :class:`.Wire` mapped on this link
                                retrieved by :class:`.Service_Definition`.
        link_binding (:class:`udp_binding`): UDP binding
    """
    id_counter = 0

    def __init__(self, name, sp, tp, throughput, latency):
        self.name = name
        self.source_platform = sp
        self.target_platform = tp
        self.throughput = throughput
        self.latency = latency
        self.id = PlatformLink.id_counter

        self.protocol = ""
        self.link_binding = None

        self.service_syntax = OrderedDict() # service_definition => list of wire

        PlatformLink.id_counter = PlatformLink.id_counter + 1

    def get_id(self):
        return self.id

    def get_name(self):
        return self.__repr__()

    def get_source_platform(self):
        return self.source_platform

    def get_target_platform(self):
        return self.target_platform

    def get_throughput(self):
        return self.throughput

    def get_latency(self):
        return self.latency

    def __repr__(self):
        return self.source_platform + ':' + \
               self.target_platform




    def find_services_wires(self, PF_wire_mapping, components, component_types, service_definitions):
        if self.name not in PF_wire_mapping:
            # no wire map on this PF link
            return

        for wire in PF_wire_mapping[self.name]:
            syntax_service = wire.find_service_syntax(components, component_types, service_definitions)
            if syntax_service not in self.service_syntax:
                self.service_syntax[syntax_service]=[]
            self.service_syntax[syntax_service].append(wire)




    def get_other_platform(self, platform_name):
        """return the other pfatform name or "" if the platform_name is neither source or target
        """

        if self.source_platform == platform_name:
            return self.target_platform
        elif self.target_platform == platform_name:
            return self.source_platform
        else:
            return ""
