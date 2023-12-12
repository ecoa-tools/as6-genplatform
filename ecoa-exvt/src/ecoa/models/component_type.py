# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

from .property_type import Property_Type
from ..utilities.logs import error, warning
from collections import OrderedDict

class Service_Instance:
    """Describes an instance of a service used in a component type

    Attributes:
        name         (str) : service name
        id           (int) : id
        syntax       (str) : service syntax name
        qos          (str) : name of quality service of this service
        socket_index (int) : socket number of this service. Will be used in C code as index
                             in an array
        is_reference (bool): True if it is a reference, False if it is a service
    """
    id_counter = 0

    def __init__(self, name, syntax, socket_number, is_reference, qos=""):
        self.name = name
        self.id = Service_Instance.id_counter
        self.syntax = syntax
        self.qos = qos
        self.socket_index = socket_number
        Service_Instance.id_counter = Service_Instance.id_counter + 1
        self.is_reference = is_reference

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_syntax(self):
        return self.syntax

    def get_qos(self):
        return self.qos


class Component_Type:
    """Describes an instance of component used within an assembly schema

    Attributes:
        name       (str) : name of component type
        id         (int) :
        services   (list): list of provided services (:class:`.Service_Instance`)
        references (list): list of required references (:class:`.Service_Instance`)
        properties (dict): dictionary of :class:`.Property_Type` retrieved by name
    """
    id_counter = 0

    def __init__(self, name):
        self.name = name
        self.id = Component_Type.id_counter
        self.services = []
        self.references = []
        self.properties = OrderedDict()
        Component_Type.id_counter = Component_Type.id_counter + 1

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def add_service(self, service_name, syntax, socket_number, qos):
        """Add a service to the component type

        Args:
            service_name (str): name of new :class:`.Service_Instance`
            syntax       (str): syntax of new service
            socket_number(int): port number of the new service
            qos          (str): name of the quality of service of the new service

        Returns:
            bool:

        Note:
            Enforce only one instance of one given type
        """
        if service_name in self.services:
            warning("Service %s already provided by %s" % (service_name, self.name))
            return False
        else:
            s = Service_Instance(service_name, syntax, socket_number, False, qos)
            self.services.append(s)
            return True

    def add_reference(self, service_name, syntax, socket_number, qos):
        """Add a reference to the component type

        Args:
            service_name (str): name of new :class:`reference <.Service_Definition>`
            syntax       (str): syntax of new reference
            socket_number(int): port number of the new reference
            qos          (str): name of the quality of service of the new reference


        Returns:
            bool:

        Note:
            Enforce only one instance of one given type
        """
        if service_name in self.references:
            warning("Service %s already provided by %s" % (service_name, self.name))
            return False
        else:
            s = Service_Instance(service_name, syntax, socket_number, True, qos)
            self.references.append(s)
            return True

    def add_property(self, prop_name, prop_type, libraries):
        if prop_name in self.properties:
            error("Property "+ prop_name + " already exist in component type "+self.name)
        else:
            self.properties[prop_name] = Property_Type(prop_name, prop_type, libraries)

    def find_service_syntax(self, serv_ref_name):
        """get the syntax name of service/reference name in this component type

        Args:
            serv_ref_name  (str): The service/reference name

        Return:
            str: the syntax name
        """
        for s in self.services:
            if s.name == serv_ref_name:
                return s.syntax
        for f in self.references:
            if f.name == serv_ref_name:
                return f.syntax

    def to_string(self):
        string = ""
        string += "Component type: " + self.name+"\n"
        string += "  services:" +str(self.services)+"\n"
        string += "  references: "+str(self.references)+"\n"
        string += "  properties: "+str(list(self.properties.keys()))+"\n"

        return string
