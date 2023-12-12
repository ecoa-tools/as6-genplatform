# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

from ..utilities.logs import error
import re
from collections import OrderedDict

class Data_Type:
    """Data type class with :class:`.Library`

    Attributes:
        id              (int)        : id
        name            (str)        : type name
        data_category   (str)        : ecoa category ('SIMPLE', 'RECORD', 'VARIANT_RECORD',
                                                        'ARRAY', 'FIXED_ARRAY', 'ENUM', 'CONSTANT')
        data_type       (str)        : data type used for 'SIMPLE', 'CONSTANT', 'ARRAY' or 'ENUM'
        parser          (elementTree): elementTree element. NOT USED
        lib_name        (str)        : name of the library
    """
    id_counter = 0

    def __init__(self, name, lib_name, data_category="", data_type="", parser=None, type_comment=""):
        self.name = name
        self.id = Data_Type.id_counter
        self.data_category = data_category
        self.data_type = data_type
        self.parser = parser
        self.lib_name = lib_name
        self.comment = type_comment
        Data_Type.id_counter = Data_Type.id_counter + 1

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_data_category(self):
        return self.data_category

    def get_data_type(self):
        return self.data_type

    def get_parser(self):
        return self.parser

    def is_complex_type(self):
        """
        :return: True if Data_Type is complex (ie: 'ARRAY', 'FIXED_ARRAY','RECORD' or 'VARIANT_RECORD'), False otherwise
        """
        return self.data_category in ['ARRAY', 'FIXED_ARRAY', 'RECORD', 'VARIANT_RECORD']

    def _find_dtype(self, datatype_name, libraries):
        lib_name, type_name = datatype_name.split(":")
        next_datatype = libraries[lib_name][0].datatypes2[type_name]
        return next_datatype

    def evaluate_string_value(self, string_value, libraries):
        """from a string that contains a constant reference or a string for a integer, a float, an hexa char or a char

        Args:
            string_value (str): string to evaluate
            libraries   (dict):

        Returns:
            : value of this string as an integer or a float number
        """
        cst_value = 0
        if string_value.find("%") != -1: # constant
            cst_data_type = self._find_dtype(string_value.replace("%",""), libraries)
            cst_value = cst_data_type.evaluate_string_value(cst_data_type.value_str,libraries)
        elif string_value[0:2] == '0x':
            cst_value = int(string_value, 16) # character in hexa to integer
        elif re.search(r'^[a-zA-Z]{1}$',string_value):
            cst_value = int(hex(ord(string_value)),16) # character to an integer
        elif re.search(r'^[0-9]+$', string_value): # integer string to integer
            cst_value = int(string_value)
        elif re.search(r'^[0-9]+.[0-9]+$', string_value): # float string to float
            cst_value = float(string_value)
        else:
            cst_value = None
            pass
        return cst_value

    def fix_data_type(self, lib, ecoa_lib):
        """Fix data type name. add library name and ':' if missing

        Args:
            lib      (:class:`.Library`): the library of the Data_Type object
            ecoa_lib (:class:`.Library`): ECOA Library
        """
        if self.data_type.find(':') == -1 and self.data_type != "PREDEF":
            if self.data_type in lib.datatypes2:
                self.data_type = lib.name + ':' + self.data_type
            elif self.data_type in ecoa_lib.datatypes2:
                self.data_type = 'ECOA:'+ self.data_type


class Simple_Data_type(Data_Type):
    """Class based on :class:`.Data_Type` to describe an Simple type

    Attributes:
        min_range  (str):
        max_range  (str):
    """
    def __init__(self, name, lib_name, data_category="", data_type="", parser=None, type_comment=""):
        Data_Type.__init__(self, name, lib_name, data_category, data_type, parser, type_comment)
        self.min_range = ""
        self.max_range = ""
        self.precision = None

    def fix_data_type(self, lib, ecoa_lib):
        """Fix data type name: add library name and ':' if missing.
        Fix min_range and max_range: fix string if it is a Constant or the string value if it is a ECOA:char8

        Args:
            lib      (:class:`.Library`): the library of the Data_Type object
            ecoa_lib (:class:`.Library`): ECOA Library
        """
        Data_Type.fix_data_type(self, lib, ecoa_lib)

        if self.min_range.find('%') != -1: # refer to a constant
            self.min_range = lib.fix_constant(self.min_range, ecoa_lib)
        else:
            if re.search(r'^[a-zA-Z]{1}$',self.min_range) != None:
                # fix character value
                self.min_range = "\'"+self.min_range+"\'"

        if self.max_range.find('%') != -1: # refer to a constant
            self.max_range = lib.fix_constant(self.max_range, ecoa_lib)
        else:
            if re.search(r'^[a-zA-Z]{1}$',self.max_range) != None:
                self.max_range = "\'"+self.max_range+"\'"


    def find_predefined_type(self, libraries):
        """Find the ECOA predefined type of this simple type

        Return:
            (:class:`.Data_Type`): The ECOA data type or None if Deadlock detected (loop definition)
        """
        next_datatype = self
        dict_datatype = set() # to avoid deadlock
        while(True):
            if next_datatype.lib_name == 'ECOA':
                break
            else:
                if next_datatype.data_type not in dict_datatype:
                    dict_datatype.add(next_datatype.data_type)
                else:
                    error("DEADLOCK: due to type definition "+ next_datatype.name)
                    return None
                lib_name, type_name = next_datatype.data_type.split(":")
                next_datatype = libraries[lib_name][0].datatypes2[type_name]

        return next_datatype



class Array_Data_type(Data_Type):
    """Class based on :class:`.Data_Type` to describe an ARRAY type

    Attributes:
        max_number (str): string to describe the size of the array. Coulb be an interger or a constant
    """
    def __init__(self, name, lib_name, data_category="", data_type="", parser=None, type_comment=""):
        Data_Type.__init__(self, name, lib_name, data_category, data_type, parser, type_comment)
        self.max_number = ""

    def fix_data_type(self, lib, ecoa_lib):
        """Fix item data type name: add library name and ':' if missing.
        Fix max_number: fix string if it is a Constant.

        Args:
            lib      (:class:`.Library`): the library of the Data_Type object
            ecoa_lib (:class:`.Library`): ECOA Library
        """

        Data_Type.fix_data_type(self, lib, ecoa_lib)

        # fix max_number string
        if self.max_number.find('%') != -1: # refer to a constant
            self.max_number = lib.fix_constant(self.max_number, ecoa_lib)


class Constant_Data_type(Data_Type):
    """Class based on :class:`.Data_Type` to describe a CONSTANT type

    Attributes:
        value_str (str): string of the value of the constant. Could be a number, an Enum or an other constant
    """
    def __init__(self, name, lib_name, data_category="", data_type="", parser=None, type_comment=""):
        Data_Type.__init__(self, name, lib_name, data_category, data_type, parser, type_comment)
        self.value_str=""

    def fix_data_type(self, lib, ecoa_lib):
        """
        """
        Data_Type.fix_data_type(self, lib, ecoa_lib)

        if self.value_str.find('%') != -1: # refer to a constant
            self.value_str = lib.fix_constant(self.value_str, ecoa_lib)

        else:
            if re.search(r'^[a-zA-Z]{1}$',self.value_str) != None:
                # fix character value
                self.value_str = "\'"+self.value_str+"\'"

class Enum_Data_Type(Data_Type):
    """Class based on :class:`.Data_Type` to describe an ENUM type

    Attributes:
        enum_list  (list): list of dictionary for each enum field
            * "name" : field name
            * "value" : field value as string (could be a constant) after calling evaluate_empty_value : become an Integer value
            * "comment" : comment
    """
    def __init__(self, name, lib_name, data_category="", data_type="", parser=None, type_comment=""):
        Data_Type.__init__(self, name, lib_name, data_category, data_type, parser, type_comment)
        self.enum_list = []

    def fix_data_type(self, lib, ecoa_lib):
        """Fix data type name: add library name and ':' if missing.
        Fix value of each enum field: if it refers to a constant, fix constant name

        Args:
            lib      (:class:`.Library`): the library of the Data_Type object
            ecoa_lib (:class:`.Library`): ECOA Library
        """
        Data_Type.fix_data_type(self, lib, ecoa_lib)

        # fix constant value
        for enum in self.enum_list:
            if enum["value"] != None and not enum["value"].isdigit():
                enum["value"]= lib.fix_constant(enum["value"], ecoa_lib)


    def add_enum_value(self, enum_name, enum_value, enum_comment):
        self.enum_list.append({"name" : enum_name, \
                               "value" : enum_value, \
                               "comment" : enum_comment})


    def evaluate_empty_value(self, libraries):
        """Rewrite enum_list to change value of fields in Integer value

        Args:
            libraries (list): list of :class:`.Library`
        """
        previous_value = -1
        for index, enum in enumerate(self.enum_list):
            if enum["value"] is None:
                # if value is not defined
                previous_value += 1
                enum["value"]=str(previous_value)
            else:
                previous_value = self.evaluate_string_value(enum["value"], libraries)


class Record_Data_Type(Data_Type):
    """Class based on :class:`.Data_Type` to describe a RECORD type

    Attributes:
        field_list  (list): list of dictionary for each record field:

            * "name" : field name
            * "type_name" : type name of the field
            * "comment" : comment
    """
    def __init__(self, name, lib_name, data_category="", data_type="", parser=None, type_comment=""):
        Data_Type.__init__(self, name, lib_name, data_category, data_type, parser, type_comment)
        self.field_list=[]

    def add_field (self, field_name, field_type_name, field_comment):
        self.field_list.append({'name' : field_name,
                                'type_name' : field_type_name,
                                'comment' : field_comment})

    def fix_data_type(self, lib, ecoa_lib):
        for field in self.field_list:
            field["type_name"]= lib._fix_data_type2(field["type_name"], ecoa_lib)


class Var_Record_Data_Type(Record_Data_Type):
    """Class based on :class:`.Record_Data_Type` to describe a VARIANT type

    Attributes:
        union_list  (list): list of dictionary for each union field :

            * "name" : field name
            * "type_name" : type name of the field
            * "comment" : comment
        selector (dict):
            * "name" : selector name
            * "type_name" : type name of the selector
    """
    def __init__(self, name, lib_name, data_category="", data_type="", parser=None, type_comment=""):
        Record_Data_Type.__init__(self, name, lib_name, data_category, data_type, parser, type_comment)
        self.union_list=[]
        self.selector=OrderedDict()

    def add_union_field (self, union_name, union_type_name, union_comment, union_when):
        self.union_list.append({'name' : union_name,
                                'type_name' : union_type_name,
                                'comment' : union_comment,
                                'when' : union_when})

    def add_selector(self, selector_name, selector_type_name):
        self.selector={'name' : selector_name,
                     'type_name' : selector_type_name}

    def fix_data_type(self, lib, ecoa_lib):
        Record_Data_Type.fix_data_type(self, lib, ecoa_lib)

        self.selector['type_name'] = lib._fix_data_type2(self.selector["type_name"], ecoa_lib)

        for union_field in self.union_list:
            union_field["type_name"]= lib._fix_data_type2(union_field["type_name"], ecoa_lib)
            if union_field["when"].find('%') != -1: # refer to a constant
                union_field["when"] = lib.fix_constant(union_field["when"], ecoa_lib)
            elif re.search( r"^(0x)?[0-9a-fA-F]+$",union_field["when"] ) is not None: # is digit or hexa
                pass
            elif re.search( r"^[a-zA-Z]{1}$",union_field["when"] ) is not None: # only one char
                # change character in an hexadecimal number string
                union_field["when"]= str(hex(ord(union_field["when"])))
            else: # refer to an enum
                if union_field["when"].find(":") != -1:
                    union_field["when"] = union_field["when"].split(':')[-1] # remove enum name. keep only the select name


    def find_minimal_union_field(self, libraries):
        """Find the union field with the minimal selector value
        """
        selector_type = self._find_dtype(self.selector["type_name"], libraries)
        u_field_found = None
        if selector_type.data_category == 'ENUM':
            # if selector if an ENUM type

            if self.selector["type_name"] == 'ECOA:boolean8':
                # case of ECOA:boolean.
                u_field_found = next( u for u in self.union_list if u["when"].find('FALSE') != -1)
                if u_field_found == None:
                    u_field_found = next( u for u in self.union_list if u["when"].find('TRUE') != -1)

            else:
                # normal ENUM
                # enum_list should be sort from the minimal to the maximal value
                for enum in selector_type.enum_list:
                    # find an union field that used this enum a selector value
                    for u_field in self.union_list:

                        if enum["name"] == u_field["when"]:
                            # if it is the same enum
                            u_field_found = u_field
                            break
                        else:
                            # try to evaluate the value of the enum and the field
                            enum_value = self.evaluate_string_value(enum["value"], libraries)
                            u_field_value = self.evaluate_string_value(u_field["when"], libraries)
                            if enum_value == u_field_value:
                                u_field_found = u_field
                                assert(enum_value != None)
                                break

                    if u_field_found != None:
                        break

        else:
            # selector type is integer
            u_field_found = self.union_list[0]
            min_val = self.evaluate_string_value(u_field_found["when"], libraries)
            for u_field in self.union_list:
                u_value = self.evaluate_string_value(u_field["when"], libraries)
                if u_value < min_val:
                    min_val = u_value
                    u_field_found = u_field

        assert(u_field_found != None)
        return u_field_found


