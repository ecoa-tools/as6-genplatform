# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

class Property_Type:
    """Module property type

    Attributes:
        id   (int)
        name (str)
        type (str)
    """
    id_counter = 0

    def __init__(self, prop_name, prop_type, libraries):
        self.name = prop_name
        self.id = Property_Type.id_counter
        self.type = prop_type
        self.data_type = None

        Property_Type.id_counter += 1

        self.__update_type(libraries)

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_type(self):
        if self.data_type is None:
            return None
        if self.data_type.data_category == 'CONSTANT':
            return self.data_type.data_type
        else:
            return self.type

    def __str__(self):
        if self.type is None:
            return self.name
        return self.name + ", "+self.type

    def __update_type(self, libraries):
        if self.type is None:
            return
        if self.type.find(":") == -1:
            self.type = 'ECOA:'+self.type
        library_name, type_name = self.type.split(":", 1)

        # set data_type if possible
        if library_name in libraries:
            if libraries[library_name][0].is_datatype_defined(type_name):
                self.data_type = libraries[library_name][0].get_data_type(type_name)
