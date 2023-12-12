# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

class Pinfo:
    """ Pinfo

    Attributes:
        name        (str) : parameter name
        pinfo_value        (str)  : parameter type
        is_private  (bool): True if parameter type is a complex type (ie: a pointer will be used)
        index       (str) : index of Pinfo in component implementation
        direction   (str) : 'input' or 'output'
    """

    def __init__(self, pinfo_name, pinfo_value, is_private, pinfo_index):
        self.name = pinfo_name
        self.pinfo_value = pinfo_value
        self.is_private = is_private
        self.index = pinfo_index
        self.directory = ""

    def get_pinfo_value(self, component_properties):
        value = ""
        if self.is_private:
            value = self.pinfo_value
        else:
            value = self.pinfo_value
            if value[0] == '$':
                # reference to a component property
                value = component_properties[value[1:]].evaluate_property()
        return value

