# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

"""
Comparaison functions of Library
"""

from ecoa.utilities.logs import warning
from .utils_comparator import compare_set

def datatype_comparator(msg, type_1, type_2):
    """Compare 2 datatypes"""

    msg = "datatype '%s, "%type_1.name + msg

    # category
    if type_1.data_category != type_2.data_category:
        warning("[DIFF] category '%s' != '%s', "%
                (type_1.data_category, type_2.data_category)+msg)
        return

    #type
    if type_1.data_type != type_2.data_type:
        warning("[DIFF] type '%s' != '%s', "%(type_1.data_type, type_2.data_type)+msg)
        return

    #
    if type_1.data_category == 'SIMPLE':
        # check min_range, max_range, precision
        if type_1.min_range != type_2.min_range:
            warning("[DIFF] min_range, '%s' != '%s', "%
                    (type_1.min_range, type_2.min_range)+msg)
        if type_1.max_range != type_2.max_range:
            warning("[DIFF] max_range, '%s' != '%s', "%
                    (type_1.max_range, type_2.max_range)+msg)
        if type_1.precision != type_2.precision:
            warning("[DIFF] precision, '%s' != '%s', "%
                    (type_1.precision, type_2.precision)+msg)

    elif type_1.data_category in ['RECORD','VARIANT_RECORD']:
        # check field order and field concistency
        if len(type_1.field_list) != len(type_2.field_list):
                warning("[DIFF] structures are different (values number), "+msg)

        for field_1, field_2 in zip(type_1.field_list, type_2.field_list):
            if field_1["name"] != field_2["name"] or\
               field_1["type_name"] != field_2["type_name"]:
                warning("[DIFF] structure fields are different (type_anme or name), "+msg)
        # TODO var_reccord

    elif type_1.data_category in ['ARRAY', 'FIXED_ARRAY']:
        # check array size
        if type_1.max_number != type_2.max_number:
            warning("[DIFF] size, '%s' != '%s', "%
                    (type_1.max_number, type_2.max_number)+msg)

    elif type_1.data_category == 'ENUM':
        # check value order and consistency
        if len(type_1.enum_list) != len(type_2.enum_list):
                warning("[DIFF] enums are different (values number), "+msg)

        for e1, e2 in zip(type_1.enum_list, type_2.enum_list):
            if e1["name"] != e2["name"] or\
               e1["value"] != e2["value"]:
                warning("[DIFF] enum values are different (value or name), "+msg)

    elif type_1.data_category == 'CONSTANT':
        # check value
        if type_1.value_str != type_2.value_str:
            warning("[DIFF] value, '%s' != '%s', "%
                    (type_1.value_str, type_2.value_str)+msg)


def libraries_comparator(model_1_name, model_2_name, lib_1, lib_2):
    """Compare 2 Libraries"""

    # find missing datatypes
    intersection_dname = compare_set("in library '%s', " % lib_1.name +
                                     "following datatypes are not defined",
                                     model_1_name,
                                     model_2_name,
                                     set(lib_1.datatypes2.keys()),
                                     set(lib_2.datatypes2.keys()))
    # For datatypes defined in both side: check consistency
    for dt_name in intersection_dname:
        datatype_comparator("in library '%s'" % (lib_1.name),
                            lib_1.datatypes2[dt_name],
                            lib_2.datatypes2[dt_name])
