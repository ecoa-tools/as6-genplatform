# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

from ..utilities.logs import error, warning
from collections import OrderedDict
from .data_types import Enum_Data_Type, Record_Data_Type, Var_Record_Data_Type, Constant_Data_type, Array_Data_type,\
    Simple_Data_type, Data_Type


class Library:
    """
    Describes a datatypes library

    Attributes:
        id         (int) :
        name       (str) : library name
        datatypes  (list): list of :class:`.Data_Type`
        datatypes2 (dict): dictionary of :class:`.Data_Type` from `datatypes` retrieved by name
        included_libs (list): list of include library names
        comp_prefix         (str): string for prefix in compare function names
        comp_suffix         (str): string for suffix in compare function names
        zeroise_prefix         (str): string for prefix in initialized function names
        zeroise_suffix         (str): string for suffix in initialized function names
    """
    id_counter = 0

    def __init__(self, name, libfile_dir):
        self.name = name
        self.id = Library.id_counter
        self.libfile_directory = libfile_dir
        self.datatypes = []
        self.datatypes2 = OrderedDict()
        self.included_libs = []
        self.namespaces = name.split('.')
        Library.id_counter = Library.id_counter + 1

        self.comp_prefix="LDP"
        self.comp_suffix="compare"
        self.zeroise_prefix="LDP"
        self.zeroise_suffix="zeroise"
        self.epsilon="0.0"

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def add_datatype(self, data_type_name, data_category, data_type, parser, type_comment):
        """Add a data type for this library

            :param str data_type_name: type name of this data
            :param str data_category: ecoa category ('SIMPLE', 'RECORD', 'VARIANT_RECORD', 'ARRAY',
                                                        'FIXED_ARRAY', 'ENUM', 'CONSTANT')
            :param parser: elementTree element
        """
        # Enforce that all data types have different names
        if data_type_name in self.datatypes2:
            # self.is_datatype_defined(data_type_name) == True:
            warning(("Data type %s already defined in %s" % (data_type_name, self.name)))
            return False
        else:
            if data_category == 'ENUM':
                dt = Enum_Data_Type(data_type_name, self.name, data_category, data_type, parser, type_comment)
            elif data_category == 'RECORD':
                dt = Record_Data_Type(data_type_name, self.name, data_category, data_type, parser, type_comment)
            elif data_category == 'VARIANT_RECORD':
                dt = Var_Record_Data_Type(data_type_name, self.name, data_category, data_type, parser, type_comment)
            elif data_category == 'CONSTANT':
                dt = Constant_Data_type(data_type_name, self.name, data_category, data_type, parser, type_comment)
            elif data_category in ['ARRAY', 'FIXED_ARRAY']:
                dt = Array_Data_type(data_type_name, self.name, data_category, data_type, parser, type_comment)
            elif data_category == 'SIMPLE':
                dt = Simple_Data_type(data_type_name, self.name, data_category, data_type, parser, type_comment)
            else:
                dt = Data_Type(data_type_name, self.name, data_category, data_type, parser, type_comment)

            self.datatypes.append(dt)
            self.datatypes2[data_type_name] = dt
            return True

    def _fix_data_type2(self,data_type, ecoa_lib):
        """Fix data type name by adding library name if necessary.

        Args:
            data_type  (str): name of :class:'.Data_Type'
            ecoa_lib   (class:`.Library`):
        """
        if data_type.find(':') == -1 and data_type != "PREDEF":
            if data_type in self.datatypes2:
                data_type = self.name + ':' + data_type
            elif data_type in ecoa_lib.datatypes2:
                data_type = 'ECOA:'+ data_type
            else:
                error(data_type + " is defined neither ECOA nor in "+self.name)

        return data_type


    def fix_constant(self, cxt_value, ecoa_lib):
        """Fix constant name by adding libary name. Final constant name format is '%lib_name:cst_name%'

        Args:
            ctx_value  (str): contante name
            ecoa_lib   (:class:`.Library`): ecoa library

        Return:
            fixed constant name
        """

        cxt_value = str.replace(cxt_value, '%', '')
        cxt_value = self._fix_data_type2(cxt_value, ecoa_lib)
        return "%"+cxt_value+"%"

    def fix_all_type_names(self, ecoa_lib):
        """fix data type names in every data type of the library by adding libary nam. Final data type name format is 'lib_name:data_type_name'

        Args:
            ecoa_lib (:class:`.Library`):ecoa library
        """
        for dtype in self.datatypes2.values():
            dtype.fix_data_type(self, ecoa_lib)


    def is_datatype_defined(self, data_type_name):
        """Check if the data type name is in the datatype

        Args:
            data_type_name (str): name of a data type

        Return:
            bool: True or False
        """
        return data_type_name in self.datatypes2

    def get_data_type(self, data_type_name):
        """get Data_Type object from a name in datatypes

        Args:
            data_type_name (str) : name of data type to find

        Return:
            :class:`.Data_Type`
        """
        if data_type_name in self.datatypes2:
            return self.datatypes2[data_type_name]
        else:
            return None

    def add_included_lib(self, included_lib_name):
        if included_lib_name != 'ECOA':
            self.included_libs.append(included_lib_name)

    def get_data_category(self, libraries, dtype_name):
        """get category of a data type

        Args:
            libraries  (list): list of :class;`.Libraries`
            data       (str) : name of the data type (lib_name:type_name)

        Return:
            (str) category of data^type
        """
        lib_name, data_name = dtype_name.split(":")
        return libraries[lib_name][0].datatypes2[data_name].data_category
