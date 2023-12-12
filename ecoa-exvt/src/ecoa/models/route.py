# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

from collections import OrderedDict


class route:
    """This class contains information to create route.c file

        :param dict id_event_dict: dictionary of ID for operations of each wire. keys :
                                    wire_name+op_name ; value : ID
        :param set wires: set of wires
        :param service_definitions:
        :param dict component_implementations: dictionary of
                            :class:`~ecoa.models.component_implementation.Component_Implementation`
                            objects retrieved by name
    """

    def __init__(self, wires, components, component_types, service_definitions,
                 component_implementations, EUIDs):
        # contains ID for operations of each wire. keys : wire_name+op_name ; value : ID
        self.id_event_dict = OrderedDict()
        self.wires = wires
        self.components = components
        self.component_types = component_types
        self.component_implementations = component_implementations
        self.service_definitions = service_definitions
        self.IDs = EUIDs

        # fill dictionary id event
        # key : ID_#source_component_name#_#service_name#__#target_component_name
        # #_#service_target_name#__#operation_name#
        # value : event id
        ID = 100
        source_event_dict = OrderedDict()
        target_event_dict = OrderedDict()
        for comp in components.values():
            # c=comp.get_component_type()
            # cc=component_types[comp.get_component_type()]
            for reference_def in component_types[comp.get_component_type()][0].references:
                for op in service_definitions[reference_def.syntax][0].operations:
                    for w in wires:
                        if (w.get_source_component() == comp.get_name()
                                and w.get_source_service() == reference_def.get_name()):
                            if (w.get_target_component() + w.get_target_service() + op.get_name()
                                    not in target_event_dict):
                                if (w.get_source_component() + w.get_source_service()
                                        + op.get_name() not in source_event_dict):
                                    self.id_event_dict[w.name() + "__" + op.get_name()] = ID
                                    self.id_event_dict[w.name() + "__" + op.get_name()] = ID
                                    target_event_dict[w.get_target_component()
                                                      + w.get_target_service()
                                                      + op.get_name()] = ID
                                    source_event_dict[w.get_source_component()
                                                      + w.get_source_service()
                                                      + op.get_name()] = ID

                                else:
                                    self.id_event_dict[w.name() + "__"
                                                       + op.get_name()] = source_event_dict[
                                        w.get_source_component() + w.get_source_service()
                                        + op.get_name()]


                                    # self.id_event_dict[w.name()+"__"+op.get_name()]=ID
                                    # target_event_dict[w.get_target_component()
                                    # +w.get_target_service()
                                    # +op.get_name()]=ID

                            else:
                                self.id_event_dict[w.name() + "__" + op.get_name()] = \
                                    target_event_dict[w.get_target_component()
                                                      + w.get_target_service() + op.get_name()]

                    ID += 1
        ID = 0
