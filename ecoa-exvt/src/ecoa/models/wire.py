# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

class Wire:
    """ Class for wire object

        :param str sc: source component name
        :param str ss: source service name
        :param str tc: target component name
        :param str ts: target service name
    """

    id_counter = 0  #: unique wire number

    def __init__(self, sc, ss, tc, ts):
        self.source_component = sc  #: (str) source component name
        self.source_service = ss  #: (str) source service name
        self.target_component = tc  #: (str) target component name
        self.target_service = ts  #: (str) target service name
        self.id = Wire.id_counter
        Wire.id_counter = Wire.id_counter + 1
        self.PF_link_id = "" #: (str) id of Platform link if this wire is mapped with an other Platform

    def __lt__(self, other):
        return self.id < other.id

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_source_component(self):
        return self.source_component

    def get_source_service(self):
        return self.source_service

    def get_target_component(self):
        return self.target_component

    def get_target_service(self):
        return self.target_service

    def name(self):
        return self.source_component + '_' + self.source_service + '__' + \
               self.target_component + '_' + self.target_service

    def __repr__(self):
        return self.source_component + '/' + self.source_service + ':' + \
               self.target_component + '/' + self.target_service

    def __eq__(self, other):
        return self.source_component == other.source_component and \
               self.source_service   == other.source_service and \
               self.target_component == other.target_component and \
               self.target_service   == other.target_service

    def __hash__(self):
        return  hash((self.source_component,
                      self.source_service,
                      self.target_component,
                      self.target_service,
                      self.id))

    def is_map_on_PF_link(self):
        return (self.PF_link_id != "")

    def set_wire_mapping(self, wireMapping):
        """
        if this wire is map on a platfrom link, find the ID of the PF link
        """
        for PF_link_id, wire_list in wireMapping.items():
            if self in wire_list:
                self.PF_link_id = PF_link_id
                break

    def find_service_syntax(self, components, component_types, service_definitions):
        """
        find the corresponding syntax of this wire.
        wire should be connected at least one component in components dictionary
        """
        connected_component = None
        service_name = ""
        if self.source_component in components:
            connected_component = components[self.source_component]
            service_name = self.source_service
        elif self.target_component in components:
            connected_component = components[self.target_component]
            service_name = self.target_service
        else:
            # no syntax found
            return None

        syntax_name = component_types[connected_component.component_type][0].find_service_syntax(service_name)
        return service_definitions[syntax_name][0]

    def count_written_modules_num(self, is_provider_interface, components,
                                  component_implementations):
        """
        Counts the number of modules that connected to this wire (for a provider or a require of
        services) and that can send operation on this wire

        Args:
            is_provider_interface      (bool) : Indicates if it is a provider/require interface
            components                 (dict) : dictionary of the components (:class:`.Component`)
            component_implementations  (dict) : dictionary of the component implementations
                                                (:class:`.Component_Implementation`)

        Return:
            (int) Number of connected modules
        """
        if is_provider_interface:
            comp = components[self.target_component]
            service_name = self.target_service
        else:
            comp = components[self.source_component]
            service_name = self.source_service

        if comp.component_implementation == "":
            # component is not deployed in this platform
            return 0


        comp_impl, _ = component_implementations[comp.component_implementation]

        sender_mod_dict = set()
        connected_links = [l for l in comp_impl.links
                           if service_name == l.target or service_name == l.source]
        for l in connected_links:
            if service_name == l.target:
                mod_name = l.source
                mod_op_name = l.source_operation
            else:
                mod_name = l.target
                mod_op_name = l.source_operation

            mod_inst = comp_impl.get_instance(mod_name)

            #check if operation is an output operation
            #if mod_op_name in mod_inst.out_points_dict:
            sender_mod_dict.add(mod_name)

        return len(sender_mod_dict)
