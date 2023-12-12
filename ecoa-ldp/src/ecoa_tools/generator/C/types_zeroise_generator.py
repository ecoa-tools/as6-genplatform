# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

import os
from ecoa_genplatform.generators.fix_names import fix_C_libname, fix_C_constant_value
from ecoa_genplatform.generators.version_header_generator import generate_ldp_version_header_warning
from ecoa_genplatform.generators.force_generation import file_need_generation

zeroise_function_name_t="#PREFIX#_#LibName#__#TypeName#_#SUFFIX#"
headers_types_t="void "+zeroise_function_name_t+"(#LibName#__#TypeName# *data)"
fixed_array_function_t= "\
    int i;\n\
    for(i=0; i<#LibName#__#TypeName#_MAXSIZE; i++){\n\
        #ZeroiseElementFct#(&(*data)[i]);\n\
    }\n\
"
array_function_t= "\
    int i;\n\
    data->current_size = 0;\n\
    for(i=0; i<#LibName#__#TypeName#_MAXSIZE; i++){\n\
        #ZeroiseElementFct#(&data->data[i]);\n\
    }\n"



def generate_C_zeroise_types(directory,
                             libraries,
                             force_flag):
    for lib, lib_tree in libraries.values():
        zeroise_file_name_c = os.path.join( directory, "src-gen", lib.zeroise_prefix+"__"+fix_C_libname(lib.name)+"_types_"+lib.zeroise_suffix+".c")
        zeroise_file_name_h = os.path.join( directory, "inc-gen", lib.zeroise_prefix+"__"+fix_C_libname(lib.name)+"_types_"+lib.zeroise_suffix+".h")

        if file_need_generation(zeroise_file_name_h, force_flag):
            zeroise_file_h = open(zeroise_file_name_h, 'w')
            text = _generate_C_lib_zeroise_types_h(lib)
            print(text, file=zeroise_file_h)
            zeroise_file_h.close()

        if file_need_generation(zeroise_file_name_c, force_flag):
            zeroise_file_c = open(zeroise_file_name_c, 'w')
            text = _generate_C_lib_zeroise_types_c(lib, libraries)
            print(text, file=zeroise_file_c)
            zeroise_file_c.close()

def _generate_C_lib_zeroise_types_h(lib):
    text = generate_ldp_version_header_warning()
    text += "#ifndef "+lib.zeroise_prefix+"__"+fix_C_libname(lib.name)+"_types_"+lib.zeroise_suffix+"_H\n"
    text += "#define "+lib.zeroise_prefix+"__"+fix_C_libname(lib.name)+"_types_"+lib.zeroise_suffix+"_H\n"

    text+="#include \"stdbool.h\"\n"
    text+="#include \"ECOA.h\"\n"
    text+="#include \""+fix_C_libname(lib.name)+".h\"\n"

    for included_lib in lib.included_libs:
        text += "#include \""+fix_C_libname(included_lib)+".h\"\n"

    text += "\n"
    text += "#if defined(__cplusplus)\n"
    text += "extern \"C\" {\n"
    text += "#endif /* __cplusplus */\n"

    for datatype in lib.datatypes2.values():
        if datatype.data_category == "CONSTANT":
            continue

        tmp_text = headers_types_t.replace("#PREFIX#", lib.zeroise_prefix) \
                              .replace("#SUFFIX#", lib.zeroise_suffix) \
                              .replace("#TypeName#",datatype.name) \
                              .replace("#LibName#",fix_C_libname(lib.name))+";\n"
        if lib.name == 'ECOA' and datatype.name in ['double64', 'int64', 'uint64']:
            text += "#if defined(ECOA_64BIT_SUPPORT)\n"
            text += tmp_text
            text += "#endif /* ECOA_64BIT_SUPPORT */\n"
        else:
            text += tmp_text

    text += "\n"
    text += "#if defined(__cplusplus)\n"
    text += "}\n"
    text += "#endif /* __cplusplus */\n"
    text += "#endif /*"+lib.zeroise_prefix+"__"+fix_C_libname(lib.name)+"_types_"+lib.zeroise_suffix+"_H*/\n"

    return text

def _generate_C_lib_zeroise_types_c(lib, libraries):
    ecoa_lib = libraries["ECOA"][0]
    text = generate_ldp_version_header_warning()
    text+="#include \"stdbool.h\"\n"
    text+="#include \"ECOA.h\"\n"
    text+="#include \""+ecoa_lib.zeroise_prefix+"__ECOA_types_"+ecoa_lib.zeroise_suffix+".h\"\n"
    text+="#include \""+fix_C_libname(lib.name)+".h\"\n"
    text+="#include \""+lib.zeroise_prefix+"__"+fix_C_libname(lib.name)+"_types_"+lib.zeroise_suffix+".h\"\n"

    for included_lib_name in lib.included_libs:
        included_lib = libraries[included_lib_name][0]
        text += "#include \""+fix_C_libname(included_lib.name)+".h\"\n"
        text += "#include \""+included_lib.zeroise_prefix+"__"+fix_C_libname(included_lib.name)+"_types_"+included_lib.zeroise_suffix+".h\"\n"

    for datatype in lib.datatypes2.values():
        if datatype.data_category == "CONSTANT":
            continue

        tmp_text = headers_types_t.replace("#PREFIX#", lib.zeroise_prefix) \
                               .replace("#SUFFIX#", lib.zeroise_suffix) \
                               .replace("#TypeName#",datatype.name) \
                               .replace("#LibName#",fix_C_libname(lib.name))+"{\n"
        tmp_text += _generate_zeroise_type(datatype, lib, libraries)
        tmp_text += "}\n"

        if lib.name == 'ECOA' and datatype.name in ['double64', 'int64', 'uint64']:
            text += "#if defined(ECOA_64BIT_SUPPORT)\n"
            text += tmp_text
            text += "#endif /* ECOA_64BIT_SUPPORT */\n"
        else:
            text += tmp_text


    return text

def _find_dtype(datatype_name, libraries):
    lib_name, type_name = datatype_name.split(":")
    next_datatype = libraries[lib_name][0].datatypes2[type_name]
    return next_datatype

def _find_dtype_lib(datatype_name, libraries):
    lib_name, type_name = datatype_name.split(":")
    return libraries[lib_name][0]

def _generate_zeroise_type(datatype, lib, libraries):
    """Generate function content to zeroise a data type

    Args:
        datatype   (): The :class:`.Data_Type`
        lib        (): The current :class:`.Library`
        libraries  (dict):The dictionary of all :class:`.Library`

    Return:
        (str): string of the function content
    """
    text = ""
    if datatype.data_category == "SIMPLE":
        if datatype.min_range != "":
            text += "    *data = "+fix_C_libname(datatype.lib_name)+"__"+datatype.name + "_minRange;\n"
        else:
            dt = datatype.find_predefined_type(libraries)
            if dt.name == "boolean8":
                text += "    *data = ECOA__FALSE;\n"
            else:
                text += "    *data = ECOA__"+dt.name.upper() + "_MIN;\n"

    elif datatype.data_category in ["ARRAY","FIXED_ARRAY"]:
        elt_type = _find_dtype(datatype.data_type, libraries)
        elt_datatype_lib = _find_dtype_lib(datatype.data_type, libraries)

        if datatype.data_category == "ARRAY":
            text = array_function_t
        else:
            text = fixed_array_function_t
        zeroise_function_string = zeroise_function_name_t.replace("#TypeName#",elt_type.name) \
                                                         .replace("#LibName#", fix_C_libname(elt_datatype_lib.name)) \
                                                         .replace("#PREFIX#", elt_datatype_lib.zeroise_prefix) \
                                                         .replace("#SUFFIX#", elt_datatype_lib.zeroise_suffix)

        text = text.replace("#ZeroiseElementFct#", zeroise_function_string)
        text = text.replace("#TypeName#",datatype.name) \
                   .replace("#LibName#",fix_C_libname(lib.name))


    elif datatype.data_category in ["RECORD","VARIANT_RECORD"]:
        for field in datatype.field_list:
            f_type = _find_dtype(field["type_name"], libraries)
            ftype_lib = _find_dtype_lib(field["type_name"], libraries)
            text+="    "+zeroise_function_name_t.replace("#TypeName#",f_type.name) \
                                                .replace("#LibName#",fix_C_libname(ftype_lib.name)) \
                                                .replace("#PREFIX#", ftype_lib.zeroise_prefix) \
                                                .replace("#SUFFIX#", ftype_lib.zeroise_suffix)
            text+="(&data->"+field["name"]+");\n"

        if (datatype.data_category == "VARIANT_RECORD"):
            u_field_found = datatype.find_minimal_union_field(libraries)
            u_type = _find_dtype(u_field_found["type_name"], libraries)
            u_type_lib = _find_dtype_lib(u_field_found["type_name"], libraries)

            selector_type = _find_dtype(datatype.selector["type_name"], libraries)
            text += "    data->"+datatype.selector["name"]+" = "
            if selector_type.data_category == 'ENUM': # enum type
                if selector_type.lib_name == 'ECOA':
                    text += "ECOA__"+u_field_found["when"]+";\n"
                elif u_field_found["when"].find("%") != -1: # cst case
                    text += fix_C_constant_value(u_field_found["when"])+";\n"
                elif u_field_found["when"].isdigit(): # digit case
                    text += str(u_field_found["when"])+";\n"
                else: # normal case
                    text += selector_type.lib_name+"__"+selector_type.name +"_"+u_field_found["when"]+";\n"
            else: # constant or integer
                text += fix_C_constant_value(u_field_found["when"])+";\n"

            text += "    " + zeroise_function_name_t.replace("#TypeName#",u_type.name) \
                                                    .replace("#LibName#",fix_C_libname(u_type_lib.name)) \
                                                    .replace("#PREFIX#", u_type_lib.zeroise_prefix) \
                                                    .replace("#SUFFIX#", u_type_lib.zeroise_suffix)
            text+="(&data->u_"+datatype.selector["name"]+"."+u_field_found["name"]+");\n"


    elif datatype.data_category == 'ENUM':
        if datatype.lib_name == 'ECOA' and datatype.name == "boolean8":
            text +=  "    *data = ECOA__FALSE;\n"
        else:
            text += "    *data = "+fix_C_libname(datatype.lib_name)+"__"+datatype.name + "_" + datatype.enum_list[0]["name"]+";\n"


    # ecoa library replace
    if lib.name == "ECOA" and datatype.name in ["log", "pinfo_filename"]:
        text = text.replace("i<ECOA__pinfo_filename_MAXSIZE", "i<ECOA__PINFO_FILENAME_MAXSIZE") \
                   .replace("i<ECOA__log_MAXSIZE", "i<ECOA__LOG_MAXSIZE")
    text = text.replace("#PREFIX#", lib.zeroise_prefix) \
               .replace("#SUFFIX#", lib.zeroise_suffix)
    return text
