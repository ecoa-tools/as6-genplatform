# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

from ecoa.utilities.logs import error
from ..fix_names import fix_C_data_type, fix_C_constant_value, fix_C_libname, fix_Cpp_data_type

def property_get_function_generate(prop, mtype, mname):
    """Generate C function to get the value of a property

    Args:
        prop   (:class:`~ecoa.models.property_classes.Module_Property`): The property
        mtype  (:class:`~ecoa.models.module_type.Module_Type`)  : The module type
        mname  (str)                    : The module implementation name

    Return:
        str: C code string
    """
    text = "void " + mname + "_container__get_" + prop.name + "_value(" + mname + "__context* context, " \
           + fix_C_data_type(prop.get_type()) + "* value){\n"
    text += "    ldp_module_context* ctx = ((ldp_module_context*) context->platform_hook);\n"
    if prop.data_type.is_complex_type():
        text += "    memcpy(value, &(("+ mtype.name + "__properties*)ctx->properties)->" \
                + prop.name + ", sizeof(" + fix_C_data_type(prop.get_type()) + "));\n"
    else:
        text += "    *value = ((" + mtype.name + "__properties*)ctx->properties)->" \
                + prop.name + ";\n"
    text += "}\n\n"
    return text

def property_get_function_generate_cpp(prop, mtype, mname):
    """Generate C function to get the value of a property

    Args:
        prop   (:class:`~ecoa.models.property_classes.Module_Property`): The property
        mtype  (:class:`~ecoa.models.module_type.Module_Type`)  : The module type
        mname  (str)                    : The module implementation name

    Return:
        str: C code string
    """
    text = "void Container::get_" + prop.name + "_value(" +  fix_Cpp_data_type(prop.get_type()) + "& value){\n"
    text += "    ldp_module_context* ctx = ((ldp_module_context*) this->hook);\n"
    if prop.data_type.is_complex_type():
        text += "    memcpy(&value, &(("+mtype.name+"__properties*)ctx->properties)->"+prop.name+", sizeof("+fix_Cpp_data_type(prop.get_type())+"));\n"
    else:
        text += "    value = (("+mtype.name+"__properties*)ctx->properties)->"+prop.name+";\n"
    text += "}\n\n"
    return text

def find_data_type(data_type_name, libraries, current_lib_name):
    """Find the data_type of an array element

    Args:
        data_type_name    (str) : The data type name
        libraries         (dict): The dictionary of :class:`~ecoa.models.library.Library`
        current_lib_name  (str) : The library name of the data_type

    Return:
        :class:`ecoa.models.data_types.Data_Type`
    """
    if data_type_name.count(":"):
        lib_name, data_type_name2 = data_type_name.split(":")
        return libraries[lib_name][0].datatypes2[data_type_name2]
    else:
        if data_type_name not in libraries[current_lib_name][0].datatypes2:
            return libraries['ECOA'][0].datatypes2[data_type_name]
        else:
            return libraries[current_lib_name][0].datatypes2[data_type_name]


def find_array_substring(string_val):
    """Find the string of an array in an other string

    Args:
        string_val (str): The string that contains an array and other element.
    the first char should be a '[', the begin of the array

    Return:
        str: The array string : '[x, x, x, x]'
    """

    # remove first whitespace
    string_val = string_val.lstrip()

    open_char = 1
    array_sub_string = string_val[0]
    if string_val[0] == "[":
        # normal subarray
        for char in string_val[1:]:
            if open_char == 0:
                break
            elif char == '[':
                open_char += 1
            elif char == ']':
                open_char -= 1
            array_sub_string += char
    elif string_val[0] == '"':
        # string subarray
        array_sub_string = '"' + string_val[1:].split("\"", 1)[0] + '"'

    return array_sub_string


def generate_element_string(substring, elt_data_type):
    """Generate C string for the next element (not an array)

    Args:
        substring   (str) : The substring
        elt_data_type (:class:`~ecoa.models.data_types.Data_Type`) : The data type

    Return:
        str: element string in C
    """
    # elt_data_type = find_data_type(data_type.data_type, libraries, data_type.lib_name)

    element_val = substring.split(",")[0]
    nb_read_char = len(element_val) + 1
    element_val = element_val.lstrip().rstrip()  # remove first and last whitespace

    string_element = ""
    if elt_data_type.data_category == 'SIMPLE' or \
       elt_data_type.data_category == 'CONSTANT':
        string_element =fix_C_constant_value(element_val)

    elif elt_data_type.data_category == 'ENUM':
        string_element = fix_C_libname(elt_data_type.lib_name) + "__" + elt_data_type.name + "_" + element_val

    else:
        error("Property data type "+ elt_data_type.data_category + " is not yet implemented")

    return string_element + ",", nb_read_char


def generate_subarray(substring, data_type, libraries):
    """Generate C string for a sub array (ie: an array in a 2D array)

    Args:
        substring  (str) :The substring of the sub array
        data_type  (:class:`~ecoa.models.data_types.Data_Type`) :The data_type of the array
        libraries  (dict): The dictionary of :class:`~ecoa.models.library.Library`

    Return:
        str: C string for a sub array, number of char read in substring
    """
    subarray_data_type = find_data_type(data_type.data_type, libraries, data_type.lib_name)
    subarray_string = find_array_substring(substring)
    array_string = generate_array(subarray_string, subarray_data_type, libraries) + ","
    nb_read_char = len(subarray_string) + 1
    array_string += "\n"
    return array_string, nb_read_char


def generate_multiplier(substring, data_type, libraries, written_elt_nb):
    """Generate C string for a multiper string in an array

    Args:
        substring       (str) :The substring
        data_type       (:class:`~ecoa.models.data_types.Data_Type`) :The data type of the array
        libraries       (dict): The dictionary of `:class:`~ecoa.models.library.Library`
        written_elt_nb  (int) :The current number of element written in array

    Return:
        str: generated C string, new number of element written in array, number of char read in substring
    """
    # find repetition number
    nb_repetition_str = substring.split(":", 1)[0]
    if nb_repetition_str == "*":
        nb_repetition = int(data_type.parser.get("maxNumber")) - written_elt_nb
    else:
        nb_repetition = int(nb_repetition_str)
    nb_read_char = 1 + len(nb_repetition_str)

    elt_data_type = find_data_type(data_type.data_type, libraries, data_type.lib_name)

    # create string to repeat
    subelement = substring.split(":", 1)[1]
    # if subelement[0] == "[" :
    if elt_data_type.data_category in ['ARRAY', 'FIXED_ARRAY']:
        str_to_repetition, nb_read_char_sub = generate_subarray(subelement, data_type, libraries)
        nb_read_char += nb_read_char_sub
    else:
        str_to_repetition, nb_read_char_sub = generate_element_string(subelement, elt_data_type)
        nb_read_char += nb_read_char_sub

    # write
    written_string = ""
    for _ in range(0, nb_repetition):
        written_string += str_to_repetition
        written_elt_nb += 1

    return written_string, written_elt_nb, nb_read_char


def generate_array(string_val, data_type, libraries):
    """Generate C string for an array

    Args:
        string_val  (str): The string value
        data_type   (:class:`.Data_Type`) : The data type of the array
        libraries   (dict): The dictionary of `:class:`~ecoa.models.library.Library`

    Return:
        str: Generated C string
    """

    array_string = ""
    elt_data_type = find_data_type(data_type.data_type, libraries, data_type.lib_name)
    max_written_elt_nb = int(data_type.parser.get("maxNumber"))

    string_val = string_val.lstrip()  # remove first whitespaces
    #
    if string_val[0] == "[" and string_val[-1] == "]":
        # normal array
        string_val = string_val[1:-1]  # remove first '[' and last ']'

        # read each char exept first and last
        index = 0
        written_elt_nb = 0
        while index < len(string_val):
            # check size
            if written_elt_nb > max_written_elt_nb:
                error("Too many elements in array : " + str(array_string))
                break

            if string_val[index] in [' ', ',']:
                # do nothing in case of whitespace or comma
                subelement_read_char_nb = 1
                subelement_str = ""
            elif string_val[index] == '#':
                # multiplier case
                index += 1
                subelement_str, written_elt_nb, subelement_read_char_nb \
                    = generate_multiplier(string_val[index:], data_type, libraries, written_elt_nb)
            elif string_val[index] in ['[', '"']:
                # subarray case
                subelement_str, subelement_read_char_nb = generate_subarray(string_val[index:],
                                                                            data_type, libraries)
                written_elt_nb += 1
            else:
                # simple element
                subelement_str, subelement_read_char_nb = \
                    generate_element_string(string_val[index:], elt_data_type)
                written_elt_nb += 1

            index += subelement_read_char_nb
            array_string += subelement_str

    elif string_val[0] == "\"" and string_val[-1] == "\"" \
            and data_type.data_type in ['char8', 'ECOA:char8']:
        # string array
        array_string = string_val
        written_elt_nb = len(string_val) - 2 - string_val.count("\\")  # do count `"` char

    else:
        error("Invalid value in properties : "+string_val)
        return ""

    if data_type.data_category == 'ARRAY':
        array_string = str(written_elt_nb) + ",{" + array_string + "}"
    elif data_type.data_category == 'FIXED_ARRAY':
        if written_elt_nb != max_written_elt_nb:
            error("Incorret number of elements in array ("+str(written_elt_nb)
                + "/"+ str(max_written_elt_nb)+"): " + str(array_string))

    return "{" + array_string + "}"


def property_init_generate(prop, component, libraries):
    """Generate C code to init a property

    Args:
        prop       (:class:`~ecoa.models.property_type.Property_Type`): The property
        component  (:class:`~ecoa.models.component.Component`)    : The component
        libraries  (dict): The dictionary of :class:`~ecoa.models.library.Library`

    Return:
        str: Generated C code
    """
    text = "        ." + prop.name + " = "
    data_type = prop.property_type.data_type

    # eveluate property regarding component properties.
    prop_value = prop.evaluate_property(component.properties)

    if data_type.data_category in ['ARRAY', 'FIXED_ARRAY']:
        prop_value = generate_array(prop_value, data_type, libraries) + ","
    else:
        prop_value, _ = generate_element_string(prop_value, data_type)

    text += prop_value
    text += "\n"
    return text
