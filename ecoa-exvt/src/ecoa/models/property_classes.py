# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

from .property_type import Property_Type
from ..utilities.logs import error

class Gen_Property:
    """Generic property class

    Attributes:
        name          (str) : property name
        value         (str) : string that represents the value of this property
        property_type (:class:`.Property_Type`) : property data type
    """
    def __init__(self, name, value):
        self.name = name
        self.value = value
        self.property_type = None

    def check_property_value(self):
        """Check if the property value if empty  or not

        Return:
            bool: True if value is correct, or False
        """
        if self.value is None:
            error("In Composite Property "+ self.name + ", value is none")
            return False
        return True


class Module_Property(Gen_Property):
    """Class based on :class:`.Gen_Property` to describe a module property
    """
    def __init__(self, name, value):
        Gen_Property.__init__(self, name, value)

    def __str__(self):
        return self.name + ": "+str(self.value)

    def check_reference(self, Component_Properties):
        """Check if value is correct or not. If the value refers to a component property, check if the reference exists

        Args:
            Component_Properties  (dict): The component dictionary of :class:`.Component_Property`

        Return:
            True or False
        """
        if self.value is None:
            return False
        if self.value[0] == '$':
            if self.value[1:] not in Component_Properties:
                return False
        return True

    def evaluate_property(self, component_properties):
        """Evaluate the property value. In case of reference, return the component property value.
In normal case, return the property value.

        Args:
            component_properties  (dict): The component dictionary of :class:`.Component_Property`

        Return:
            (str): the property value (without reference)
        """
        if self.value[0] == '$':
            return component_properties[self.value[1:]].evaluate_property()
        else:
            return self.value



class Component_Property(Gen_Property):
    """Class based on :class:`.Gen_Property` to describe a component property

    Attributes:
        source                 (str): could be set if the property refers to a composite property
        composite_properties  (:class:`.Property_Type`): dictionary of :class:`.Composite_Property`
    """
    def __init__(self, name, value, source, composite_properties):
        Gen_Property.__init__(self, name, value)
        self.source = None
        self.composite_properties = composite_properties

        if source is not None:
            if source[0] == '$':
                self.source = source
            else:
                error("Component property has invalid source "+ source)

    def __str__(self):
        return self.name + ": "+str(self.value)+ ", " + str(self.source)

    def evaluate_property(self):
        """Evaluate the property value.

        In case of reference, return the composite property value.
        In normal case, return the property value.

        Return:
            str: the property value (without reference)
        """
        if self.value is None:
            if self.source[1:] not in self.composite_properties:
                error("Property source "+ self.source +" doesn't exist")
                return None
            else:
                return self.composite_properties[self.source[1:]].value
        else:
            return self.value

    def get_property_type(self):
        """
        Return:
            :class:`.Property_Type`
        """
        return self.composite_properties[self.source[1:]].type



class Composite_Property(Gen_Property):
    """Class based on :class:`.Gen_Property` to describe a composite property

    Attributes:
        property_type  (:class:`.Property_Type`):
    """
    def __init__(self, name, ptype, value, libraries):
        Gen_Property.__init__(self, name, value)
        self.property_type = Property_Type(name, ptype, libraries)

    def __str__(self):
        return self.name + ": "+str(self.value) + ", ("+ str(self.property_type.type)+")"
