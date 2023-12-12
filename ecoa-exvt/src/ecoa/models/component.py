# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

from .property_classes import Component_Property
from ..utilities.logs import error, warning
from collections import OrderedDict

class Component:
    """Describes an instance of component used within an assembly schema

    Attributes:
        id                       (int) : unique number
        name                     (str) : component name
        component_type           (str) : name of the :class:`.Component_Type`
        component_implementation (str) : name of the :class:`.Component_Implementation`
        composite_name           (str) : name of the composite (use in upper.impl.composite in case of multiplatform)
        services                 (list): provided services
        references               (list): required services
        properties               (dict): dictionary of :class:`.Component_Property`

        log_levels               (list): list of log level. All levels are accepted by default
        mod_log_levels           (dict): dictionary of log levels for each modules instance.
                                            module_name -> list of levels
        mod_protection_domain    (dict): dictionary of the protection domain for each module
                                            instance. module_name -> name of the PD
        mod_node                 (dict): dictionary of the node for each module instance.
                                            module_name -> name of the node
        mod_priority             (dict): dictionary of : module_name ->priority of module instance
        mod_relocated_priority   (dict): dictionary of : module_name ->priority of module instance

    """

    id_counter = 0  #:(int) unique number

    def __init__(self, name):
        self.name = name
        self.id = Component.id_counter
        self.component_type = ""
        self.component_implementation = ""
        self.composite_name = ""
        self.services = []
        self.service_syntaxes=OrderedDict() # TODO : add documentation : only use by upper.composite
        self.references = []
        self.reference_syntaxes=OrderedDict() # TODO : add documentation : only use by upper.composite
        self.properties = OrderedDict()


        self.log_levels = ["FATAL", "ERROR", "DEBUG", "WARN", "INFO", "TRACE"]
        self.mod_log_levels = OrderedDict()
        self.mod_protection_domain = OrderedDict()
        self.mod_node = OrderedDict()
        self.mod_priority = OrderedDict()
        self.mod_relocated_priority = OrderedDict()

        Component.id_counter = Component.id_counter + 1


    def add_property(self, name, value, source, composite_properties):
        if name in self.properties:
            error("property "+ name + " is already defined in component "+ self.name)
            return
        self.properties[name] = Component_Property(name, value, source, composite_properties)

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def set_component_type(self, ctn):
        if self.component_type != "":
            warning("Enforce new componentType %s for component %s" % (ctn, self.name))
        self.component_type = ctn
        return True

    def set_composite_name(self, name):
        self.composite_name = name

    def get_component_type(self):
        return self.component_type

    def set_component_implementation(self, cin):
        if self.component_implementation != "":
            warning("Enforce new component implementation %s for component %s" % (cin, self.name))
        self.component_implementation = cin
        return True

    def get_component_implementation(self):
        return self.component_implementation

    def add_service(self, service_name, syntax=""):
        if service_name in self.services:
            warning("Service %s already provided by %s" % (service_name, self.name))
            return False
        else:
            self.services.append(service_name)
            if syntax != "":
                self.service_syntaxes[service_name] = syntax
            return True

    def add_reference(self, service_name, syntax=""):
        if service_name in self.references:
            warning("Service %s already provided by %s" % (service_name, self.name))
            return False
        else:
            self.references.append(service_name)
            if syntax != "":
                self.reference_syntaxes[service_name] = syntax
            return True

    def get_services(self):
        return self.services

    def get_references(self):
        return self.references

    def check_service(self, service_name):
        if service_name not in self.services:
            error("Service %s not defined in component %s" % (service_name, self.name))
            return ""
        else:
            return service_name

    def check_reference(self, reference_name):
        if reference_name not in self.references:
            error("Reference %s not defined in component %s" % (reference_name, self.name))
            return ""
        else:
            return reference_name

    def is_service(self, service_name):
        return service_name in self.services

    def is_reference(self, reference_name):
        return reference_name in self.references

    def to_string(self):
        string = ""
        string += "Component: " + self.name + "\n"
        string += "  services: " + str(self.services) + "\n"
        string += "  references: " + str(self.references) + "\n"
        string += "  properties: " + str([str(p) for p in self.properties.values()]) + "\n"

        return string

    def find_connected_wires__source_service(self, wires, service_name):
        for w in wires:
            if w.source_component == self.name and w.source_service == service_name:
                return w
        return None

    def find_connected_wires__target_service(self, wires, ref_name):
        connected_wires=[]
        for w in wires:
            if w.target_component == self.name and w.target_service == ref_name:
                connected_wires.append(w)
        return connected_wires


    def find_service_target_wires(self, wires):
        """Find wires that are connected with the component.

        Args:
            wires (set): set of all :class:`.Wire`

        Returns:
            tuple of two lists of :class:`.Wire` :
                * list of wires where component is the source
                * list of wires where component is the target.
        """
        service_wires = []
        target_wires = []

        for w in wires:
            if self.get_name() == w.get_source_component():
                target_wires.append(w)
            elif self.get_name() == w.get_target_component():
                service_wires.append(w)

        return service_wires, target_wires

    def _find_PD_and_deployed_mod(self, protection_domains, mod_name, comp_name):
        """ Find the protection domain and the deployed module of a module instance in a component

        Args:
            protection_domains (dict): dictionary of all :class:`.Protection_Domain`
            mod_name           (str): name of the module instance
            comp_name     (str): name of the component instance

        Returns:
            tuple (:class:`.Protection_Domain`, :class:`Deployed_Module`):
        """
        for pd in protection_domains.values():
            if pd.is_deployed_module(comp_name, mod_name):
                return pd, pd.find_deployed_module(mod_name, comp_name)
        return None, None

    def set_log_policy(self, new_log_levels):
        """Update default log levels of modules

        Args:
            new_log_levels        (str): list of log levels separated by "|" (str)
        """
        level_list = new_log_levels.split("|")

        self.log_levels = level_list.copy()

        # add mandatory log levels:
        if "ERROR" not in self.log_levels:
            self.log_levels.append('ERROR')
        if 'FATAL' not in self.log_levels:
            self.log_levels.append('FATAL')

    def mod_set_protection_domain(self, module_name, protection_domain_name):
        """Set the name of the protection domaine for a module instance
        """
        if module_name not in self.mod_protection_domain:
            self.mod_protection_domain[module_name] = protection_domain_name
        else:
            warning(module_name + " in component " + self.name + " is already deployed")

    def mod_set_node(self, module_name, node_name):
        """Set the node name of a module instance"""
        if module_name not in self.mod_node:
            self.mod_node[module_name] = node_name
        else:
            warning(module_name + " in component " + self.name + " is already deployed")

    def mod_set_log_policy(self, mod_name, mod_log_levels):
        """Set the log levels of a module

        Args:
            mod_name       (str): module instance name
            mod_log_levels (str): list of log levels (str)
        """
        level_list = mod_log_levels.split("|")
        if "ERROR" not in level_list:
            level_list.append('ERROR')
        if 'FATAL' not in level_list:
            level_list.append('FATAL')
        if mod_name not in self.mod_log_levels:
            self.mod_log_levels[mod_name] = []
        self.mod_log_levels[mod_name] = level_list.copy()

    def mod_set_priority(self, mod_name, priority):
        """Set the priority of a module"""
        if mod_name not in self.mod_priority:
            self.mod_priority[mod_name] = priority
        else:
            warning(mod_name + " in component " + self.name + " already has priority")

    def mod_set_relocated_priority(self, mod_name, priority):
        """Set the relocated priority of a module"""
        if mod_name not in self.mod_relocated_priority:
            self.mod_relocated_priority[mod_name] = priority
        else:
            warning(mod_name + " in component " + self.name + " already has relocated priority")
