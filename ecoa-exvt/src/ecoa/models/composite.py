# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

from collections import OrderedDict

class Composite:
    """Composite class. Use for initial assembly, final assembly or upper composite at cross platform level

    Attributes:
        name                 (str) : name of the composite
        wires                (set) : set of :class:`.Wire` in the composite
        components           (dict): dictionary of :class:`.Component` defined in the composite
        properties           (dict): dictionary of :class:`.Composite_Property`
        reference_promotions (dict): dictionary of list of promotion. reference_name => list of ((comp_name, component_reference_name))
        service_promotions   (dict): dictionary of list of promotion. service_name => list of ((comp_name, component_service_name))
        is_empty             (bool): boolean that indicate if the composite is empty or not (use if upper composite is not defined)
    """
    def __init__(self, name):
        self.name = name
        self.wires = set()
        self.components = OrderedDict()
        self.properties = OrderedDict()
        self.reference_promotions = OrderedDict()
        self.service_promotions = OrderedDict()
        self.is_empty = True

    def set_name(self, name):
        self.name = name

    def add_composite_property(self, new_prop):
        if new_prop.name in self.properties:
            error("property '%s' is already defined in composite '%s'" % (new_prop.name, self.name))
            return
        self.properties[new_prop.name] = new_prop

    def add_component(self, new_comp):
        if new_comp.name in self.components:
            error("component '%s' is already exist in composite '%s'" % (new_comp.name, self.name))
            return
        self.components[new_comp.name] = new_comp

    def add_wire(new_wire):
        self.wires.add(new_wire)

    def add_reference_promotion(self, reference_name, promotion_string):
        for promote_string2 in promotion_string.split():
            comp_name, comp_ref_name = promote_string2.split("/")
            self.reference_promotions.setdefault(reference_name, []).append((comp_name, comp_ref_name))

    def add_service_promotion(self, service_name, promotion_string):
        # self.service_promotions.setdefault(service_name, []).add(promotion)
        for promote_string2 in promotion_string.split():
            comp_name, comp_serv_name = promote_string2.split("/")
            self.service_promotions.setdefault(service_name, []).append((comp_name, comp_serv_name))



    def get_component_impl(self, comp_name):
        if comp_name in self.components:
            return self.components[comp_name].get_component_implementation()
        else:
            return ""

    def get_wire_syntax(self, wire):
        comp = self.components[wire.source_component]

        if wire.source_service not in comp.service_syntaxes:
            if wire.source_service not in comp.reference_syntaxes:
                return ""
            else:
                return comp.reference_syntaxes[wire.source_service]
        else:
            return comp.service_syntaxes[wire.source_service]

    def find_promoted_service(self, component_name, service_name):
        for promoted_serv, promote_list in self.service_promotions.items():
            if (component_name, service_name) in promote_list:
                return promoted_serv
        return ""

    def find_promoted_reference(self, component_name, reference_name):
        for promoted_ref, promote_list in self.reference_promotions.items():
            if (component_name, reference_name) in promote_list:
                return promoted_ref
        return ""

    def find_promoted_services(self, component_name, service_name):
        promoted_services=set()
        for promoted_serv, promote_list in self.service_promotions.items():
            if (component_name, service_name) in promote_list:
                promoted_services.add(promoted_serv)
        return list(promoted_services)

    def find_promoted_references(self, component_name, reference_name):
        promoted_references=set()
        for promoted_ref, promote_list in self.reference_promotions.items():
            if (component_name, reference_name) in promote_list:
                promoted_references.add(promoted_ref)

        return list(promoted_references)
