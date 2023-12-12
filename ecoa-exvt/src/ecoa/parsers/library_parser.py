# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

import os
from xml.etree.ElementTree import ElementTree
from ..models.library import Library
from ..utilities.namespaces import NameSpaces, ECOS_TYPES
from ..utilities.xml_utils import validate_XML_file
from ..utilities.logs import error, info

__library_initialized = False


def __is_type_defines(ECOA_library, library, type_name):
    """Check is the name of the data type is defined in library, in namespaces, in used library, in ECOA library

    Attributes:
        ECOA_library  (:class:`~ecoa.models.library.Library`):The ECOA library
        library       (:class:`~ecoa.models.library.Library`):The library
        type_name     (str)                      :The name of :class:`~ecoa.models.data_types.Data_Type`

    Return:
        True if type defines, False otherwise.
    """

    type_name_no_namespaces = type_name.split(":")[-1]

    if library.is_datatype_defined(type_name_no_namespaces) or ECOA_library.is_datatype_defined(type_name_no_namespaces):
        return True
    else:
        return False

def __check_type_name(libraries, library, data_type_name):
    """Check if the name of the data type is defined in library, in included libraries or in ECOA library

    Attributes:
        libraries     (dict)                     : dictionary of all (:class:`~ecoa.models.library.Library`)
        library       (:class:`~ecoa.models.library.Library`): The library
        data_type_name(str)                      : The name of :class:`~ecoa.models.data_types.Data_Type`

    Return:
        True if type defines, False otherwise.
    """
    retval = False
    ECOA_library = libraries["ECOA"][0]

    if data_type_name.find(':') != -1:
        namespaces,_ = data_type_name.split(":")
        if namespaces not in libraries:
            error("Types %s, unkown namespaces %s" % (data_type_name, namespaces))

    if not __is_type_defines(ECOA_library, library, data_type_name):
        #check in included libraries
        for included_lib_name in library.included_libs:
            included_lib,_ = libraries[included_lib_name]
            if __is_type_defines(ECOA_library, included_lib, data_type_name):
                retval = True
                break
    else:
        retval = True

    if not retval:
        error("Type %s is not defined neither in %s nor in %s" % (data_type_name, library.name, str(library.included_libs)))
    return retval

def __check_record(libraries, library,dtype):
    """Check record type

    Attributes:
        libraries     (dict)                     : dictionary of all (:class:`~ecoa.models.library.Library`)
        library       (:class:`~ecoa.models.library.Library`): The library
        dtype       (:class:`~ecoa.models.data_types.Data_Type`): Data type to check

    Return:
        True if type defines, False otherwise.
    """
    retval = True
    for field in dtype.field_list:
        if not __check_type_name(libraries, library, field['type_name']):
            retval = False
    return retval

def __check_variant_record(libraries, library,dtype):
    """Check variant record type

    Attributes:
        libraries     (dict)                     : dictionary of all (:class:`~ecoa.models.library.Library`)
        library       (:class:`~ecoa.models.library.Library`): The library
        dtype       (:class:`~ecoa.models.data_types.Data_Type`): Data type to check

    Return:
        True if type defines, False otherwise.
    """
    retval = True

    if not __check_record(libraries, library,dtype):
        retval = False

    if not __check_type_name(libraries, library, dtype.selector["type_name"]):
        retval = False

    for union in dtype.union_list:
        if not __check_type_name(libraries, library, union["type_name"]):
            retval = False


    return retval


def check_type(libraries, library, dtype):
    """Check any type

    Attributes:
        libraries     (dict)                     : dictionary of all (:class:`~ecoa.models.library.Library`)
        library       (:class:`~ecoa.models.library.Library`): The library
        dtype       (:class:`~ecoa.models.data_types.Data_Type`): Data type to check

    Return:
        True if type defines, False otherwise.    """
    retval = False

    if dtype.data_category == 'VARIANT_RECORD':
        retval = __check_variant_record(libraries, library,dtype)
    elif dtype.data_category == 'RECORD':
        retval = __check_record(libraries, library,dtype)
    else:
        retval = __check_type_name(libraries, library, dtype.data_type)

    return retval


def parse_library(filename, libraries, library_name):

    if os.path.exists(filename) is False:
        error("File does not exist for %s" % (library_name))
        return
    tree = ElementTree()
    tree.parse(filename)

    library = Library(library_name, os.path.realpath(os.path.dirname(filename)))
    types_tree = tree.find(ECOS_TYPES + "types")

    if types_tree is None:
        info("No types entry in library %s" % library_name)
    else:

        # Not ordered in the right way

        for t in types_tree.iter():
            type_comment = t.get("comment", default="")
            type_name = t.get("name")
            if t.tag == ECOS_TYPES + 'simple':
                tt = t.get("type")
                library.add_datatype(type_name, 'SIMPLE', tt, t, type_comment)
                library.datatypes2[type_name].min_range = t.get("minRange", default="")
                library.datatypes2[type_name].max_range = t.get("maxRange", default="")
                library.datatypes2[type_name].precision = t.get("precision", default=None)

            if t.tag == ECOS_TYPES + 'constant':
                tt = t.get("type")
                library.add_datatype(type_name, 'CONSTANT', tt, t, type_comment)
                library.datatypes2[type_name].value_str = t.get("value")
            if t.tag == ECOS_TYPES + "record":
                tet = t.get("extends")
                if tet is not None:
                    pass
                library.add_datatype(type_name, 'RECORD', "", t, type_comment)
                dt = library.datatypes2[type_name]
                for field in t.iterfind(ECOS_TYPES + "field"):
                    field_name = field.get("name")
                    field_type_name = field.get("type")
                    field_comment = field.get("comment")
                    dt.add_field(field_name, field_type_name,field_comment)

            if t.tag == ECOS_TYPES + "variantRecord":
                library.add_datatype(type_name, 'VARIANT_RECORD', "", t, type_comment)
                dt = library.datatypes2[type_name]
                for field in t.iterfind(ECOS_TYPES + "field"):
                    field_name = field.get("name")
                    field_type_name = field.get("type")
                    field_comment = field.get("comment")
                    dt.add_field(field_name, field_type_name,field_comment)

                for union in t.iterfind(ECOS_TYPES + "union"):
                    union_type_name = union.get("type")
                    union_name = union.get("name")
                    union_comment = union.get("comment")
                    union_when = union.get("when")
                    dt.add_union_field(union_name, union_type_name, union_comment, union_when)

                selector_name = t.get("selectName")
                selector_type_name = t.get("selectType")
                dt.add_selector(selector_name, selector_type_name)

            if t.tag == ECOS_TYPES + "array":
                tt = t.get("itemType")
                library.add_datatype(type_name, 'ARRAY', tt, t, type_comment)
                library.datatypes2[type_name].max_number = t.get("maxNumber")
            if t.tag == ECOS_TYPES + "fixedArray":
                tt = t.get("itemType")
                library.add_datatype(type_name, 'FIXED_ARRAY', tt, t, type_comment)
                library.datatypes2[type_name].max_number = t.get("maxNumber")
            if t.tag == ECOS_TYPES + "enum":
                tt = t.get("type")
                library.add_datatype(type_name, 'ENUM', tt, t, type_comment)
                for vi in t.iterfind(ECOS_TYPES+"value"):
                    vname = vi.get("name")
                    vnum = vi.get("valnum")
                    vcomment = vi.get("comment", "")
                    library.datatypes2[type_name].add_enum_value(vname, vnum, vcomment)

    # Store a tuple to keep the parser
    libraries[library_name] = (library, tree)

    for lib_use in tree.iterfind(ECOS_TYPES + "use"):
        libraries[library_name][0].add_included_lib(lib_use.get("library"))


def setup_libraries(libraries):
    global __library_initialized
    if __library_initialized is None or __library_initialized is False:
        ECOA_library = Library('ECOA','')
        ECOA_library.add_datatype("boolean8", "ENUM", "PREDEF", None, "")
        ECOA_library.add_datatype("int8", "SIMPLE", "PREDEF", None, "")
        ECOA_library.add_datatype("int16", "SIMPLE", "PREDEF", None, "")
        ECOA_library.add_datatype("int32", "SIMPLE", "PREDEF", None, "")
        ECOA_library.add_datatype("int64", "SIMPLE", "PREDEF", None, "")
        ECOA_library.add_datatype("uint8", "SIMPLE", "PREDEF", None, "")
        ECOA_library.add_datatype("uint16", "SIMPLE", "PREDEF", None, "")
        ECOA_library.add_datatype("uint32", "SIMPLE", "PREDEF", None, "")
        ECOA_library.add_datatype("uint64", "SIMPLE", "PREDEF", None, "")
        ECOA_library.add_datatype("char8", "SIMPLE", "PREDEF", None, "")
        ECOA_library.add_datatype("byte", "SIMPLE", "PREDEF", None, "")
        ECOA_library.add_datatype("float32", "SIMPLE", "PREDEF", None, "")
        ECOA_library.add_datatype("double64", "SIMPLE", "PREDEF", None, "")
        ECOA_library.add_datatype("duration", "RECORD", "PREDEF", None, "")
        ECOA_library.add_datatype("global_time", "RECORD", "PREDEF", None, "")
        ECOA_library.add_datatype("hr_time", "RECORD", "PREDEF", None, "")
        ECOA_library.add_datatype("pinfo_filename", "ARRAY", "ECOA:char8", None, "")
        ECOA_library.add_datatype("log", "ARRAY", "ECOA:char8", None, "")

        for typename in ["duration", "global_time", "hr_time"]:
            dtype = ECOA_library.datatypes2[typename]
            dtype.add_field("seconds", "ECOA:uint32","")
            dtype.add_field("nanoseconds", "ECOA:uint32","")

        ECOA_library.datatypes2["pinfo_filename"].max_number = "256"
        ECOA_library.datatypes2["log"].max_number = "256"

        libraries["ECOA"] = (ECOA_library, None)
        # __library_initialized = True

def parse_all_libraries(xsd_directory, lib_files, libraries):
    retval = True

    setup_libraries(libraries)
    for filename in sorted(lib_files):
        l = str.replace(os.path.basename(filename), ".types.xml", '')
        l = l.replace("__",".") # find name space

        if os.path.exists(filename) is False:
            error("File '%s' does not exist" % (filename))
            continue

        if(validate_XML_file(filename, xsd_directory
                                 + "/Schemas_ecoa/ecoa-types-2.0.xsd") != -1):
            parse_library(filename, libraries, l)
        else:
            retval = False

    ecoa_lib = libraries['ECOA'][0]
    # set default ecoa lib
    if len(lib_files) > 0:
        # set a default directory for ECOA library with the first non-ECOA library directory
        lib = next(l for l,_ in libraries.values() if l.name != 'ECOA')
        ecoa_lib.libfile_directory = lib.libfile_directory

    for lib,_ in libraries.values():
        if lib.name != 'ECOA':
            lib.fix_all_type_names(ecoa_lib)

    for ln, ll in libraries.items():
        info("Library Name: %s %d %d" % \
              (ln, ll[0].get_id(), len(ll[0].datatypes)))

    if not check_libraries(libraries):
        retval = False

    return retval

##
## function parse_libraries
##
## Main function of this module, in correlation with services
##
def parse_libraries(directory, service_definitions, libraries):
    #TODO remove ?
    assert(0)
    ns = NameSpaces()
    ns.setup_parsing()

    setup_libraries(libraries)

    for sdn, st in service_definitions.items():
        for l in st[0].libraries:
            if l not in libraries:
                filename = directory + os.sep + l + '.types.xml'
                parse_library(filename, libraries, l)
        for op in st[0].operations:
            if op.data_type != "":
                ##check_data_type(op.data_type)
                pass
            for i in op.inputs:
                pass
            for o in op.outputs:
                pass

    for ln, ll in libraries.items():
        debug("Library Name: %s %d %d" % \
              (ln, ll[0].get_id(), len(ll[0].datatypes)))

    check_libraries(libraries)

    return True

def check_libraries(libraries):
    """Check libraries

    Attributes:
        libraries     (dict): dictionary of all (:class:`~ecoa.models.library.Library`)

    Return:
        True if all libraries are corrected, False otherwise.
    """

    retval = True
    for lib,_ in libraries.values():
        if lib.name != "ECOA":
            # check included
            for l_name in lib.included_libs:
                if l_name not in libraries:
                    error("In library %s, included library %s doesn't exist" % (lib.name, l_name))
                    retval = False

            # check types
            for dtype in lib.datatypes2.values():
                if not check_type(libraries, lib, dtype):
                    retval = False
    return retval
