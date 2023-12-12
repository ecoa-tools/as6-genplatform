# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

import os
from ecoa_genplatform.generators.fix_names import fix_C_libname, fix_C_constant_value
from ecoa_genplatform.generators.version_header_generator import generate_ldp_version_header_warning
from ecoa_genplatform.generators.force_generation import file_need_generation

def _add_64BIT_macro_protection(library, datatype, string):
    if library.name == 'ECOA' and datatype.name in ['int64', 'uint64', 'double64']:
        string_tmp="#if defined(ECOA_64BIT_SUPPORT)\n"
        string_tmp+=string
        string_tmp+="#endif /* ECOA_64BIT_SUPPORT */\n"
        string = string_tmp
    return string

headers_types_templates="bool #PREFIX#_#LibName#__#TypeName#_#SUFFIX#(const #LibName#__#TypeName# *data1, const #LibName#__#TypeName# *data2)"
def generate_C_compare_types(directory,
                             libraries,
                             force_flag):

    for lib, lib_tree in libraries.values():
        comp_file_name_c = os.path.join( directory, "src-gen", lib.comp_prefix+"__"+fix_C_libname(lib.name)+"_types_"+lib.comp_suffix+".c")
        comp_file_name_h = os.path.join( directory, "inc-gen", lib.comp_prefix+"__"+fix_C_libname(lib.name)+"_types_"+lib.comp_suffix+".h")

        if file_need_generation(comp_file_name_h, force_flag):
            comp_file_h = open(comp_file_name_h, 'w')
            text = _generate_C_lib_compare_types_h(lib)
            print(text, file=comp_file_h)
            comp_file_h.close()

        if file_need_generation(comp_file_name_c, force_flag):
            comp_file_c = open(comp_file_name_c, 'w')
            text = _generate_C_lib_compare_types_c(lib, libraries)
            print(text, file=comp_file_c)
            comp_file_c.close()


def _generate_C_lib_compare_types_h(lib):
    text = generate_ldp_version_header_warning()
    text+= "#ifndef "+lib.comp_prefix+"__"+fix_C_libname(lib.name)+"_types_"+lib.comp_suffix+"_H\n"
    text+= "#define "+lib.comp_prefix+"__"+fix_C_libname(lib.name)+"_types_"+lib.comp_suffix+"_H\n"

    text+="#include \"stdbool.h\"\n"
    text+="#include \"ECOA.h\"\n"
    text+="#include \""+fix_C_libname(lib.name)+".h\"\n"

    for included_lib in lib.included_libs:
        text += "#include \""+fix_C_libname(included_lib)+".h\"\n"

    text += "\n"
    text += "#if defined(__cplusplus)\n"
    text += "extern \"C\" {\n"
    text += "#endif /* __cplusplus */\n"
    text += "\n"

    for datatype in lib.datatypes2.values():
        if datatype.data_category != "CONSTANT":
            text_tmp= headers_types_templates.replace("#PREFIX#", lib.comp_prefix) \
                                          .replace("#SUFFIX#", lib.comp_suffix) \
                                          .replace("#TypeName#",datatype.name) \
                                          .replace("#LibName#",fix_C_libname(lib.name))+";\n"
            text+=_add_64BIT_macro_protection(lib, datatype, text_tmp)

    text += "\n"
    text += "#if defined(__cplusplus)\n"
    text += "}\n"
    text += "#endif /* __cplusplus */\n"
    text += "#endif /*"+lib.comp_prefix+"__"+fix_C_libname(lib.name)+"_types_"+lib.comp_suffix+"_H*/\n"

    return text

def _find_dtype(datatype_name, libraries):
    lib_name, type_name = datatype_name.split(":")
    next_datatype = libraries[lib_name][0].datatypes2[type_name]
    return next_datatype

def _find_selector_value(lib, svalue, selector_type):
    if svalue.find("%") == 0:
        svalue = fix_C_constant_value(svalue)
    else:
        if selector_type.data_category == "SIMPLE":
            pass
        elif selector_type.data_category == "ENUM":
            if selector_type.name == 'boolean8' and selector_type.lib_name == 'ECOA':
                svalue = "ECOA__"+svalue
            else:
                svalue = fix_C_libname(selector_type.lib_name) +"__" + selector_type.name +"_"+svalue
        else:
            assert(0)
    return svalue

def _generate_compare_if(libraries, datatype, space, variable_name1, variable_name2):
    datatype_lib = libraries[datatype.lib_name][0]

    text=space+"if("
    if datatype.is_complex_type() or _is_float(datatype, libraries[datatype.lib_name][0], libraries):
        text += "!"+datatype_lib.comp_prefix+"_"+fix_C_libname(datatype_lib.name)+"__"+datatype.name+"_"+datatype_lib.comp_suffix+"(&"+variable_name1+", &"+variable_name2+")"
    else:
        text += variable_name1+ " != "+variable_name2
    text +=')\n'
    return text

def _is_float(datatype, lib, libraries):
    value = False
    if lib.name == 'ECOA':
        if datatype.name in ['float32','double64']:
            value = True
        else:
            value = False
    else:
        if datatype.data_category == 'SIMPLE':
            # or constante? enum ?
            next_datatype = _find_dtype(datatype.data_type, libraries)
            next_lib,_ =libraries[next_datatype.lib_name]
            value = _is_float(next_datatype, next_lib, libraries)
        else:
            value = False
    return value

def _generate_C_lib_compare_types_c(lib, libraries):
    ecoa_lib = libraries["ECOA"][0]
    text = generate_ldp_version_header_warning()
    text+="#include \"stdbool.h\"\n"
    text+="#include \"ECOA.h\"\n"
    text+="#include \""+ecoa_lib.comp_prefix+"__ECOA_types_"+ecoa_lib.comp_suffix+".h\"\n"
    text+="#include \""+fix_C_libname(lib.name)+".h\"\n"
    text+="#include \""+lib.comp_prefix+"__"+fix_C_libname(lib.name)+"_types_"+lib.comp_suffix+".h\"\n"
    text+="#include <math.h>\n"


    for included_lib_name in lib.included_libs:
        included_lib = libraries[included_lib_name][0]
        text += "#include \""+fix_C_libname(included_lib.name)+".h\"\n"
        text+="#include \""+included_lib.comp_prefix+"__"+fix_C_libname(included_lib.name)+"_types_"+included_lib.comp_suffix+".h\"\n"

    text += "\n"
    for datatype in lib.datatypes2.values():
        if datatype.data_category == "CONSTANT":
            continue

        text_tmp = headers_types_templates.replace("#PREFIX#", lib.comp_prefix) \
                                       .replace("#SUFFIX#", lib.comp_suffix) \
                                       .replace("#TypeName#",datatype.name) \
                                       .replace("#LibName#",fix_C_libname(lib.name))+"{\n"
        if datatype.data_category in ['SIMPLE', 'ENUM']:
            if _is_float(datatype, lib, libraries):
                if datatype.precision != None:
                    text_tmp +="    return (fabs(*data1 - *data2) <= "+datatype.precision+");\n"
                else:
                    text_tmp +="    if ((fabs(*data1) <= 0.0) || (fabs(*data2) <= 0.0)){\n"
                    text_tmp +="        return fabs(*data1 - *data2) <= "+lib.epsilon+";\n"
                    text_tmp +="    }else{\n"
                    text_tmp +="        return (fabs(*data1 - *data2) <= "+lib.epsilon+" * fabs(*data1));\n"
                    text_tmp +="    }\n"
            else:
                text_tmp += "    return (*data1 == *data2);\n"

        elif datatype.data_category in ['FIXED_ARRAY', 'ARRAY']:
            next_datatype = _find_dtype(datatype.data_type, libraries)
            text_tmp += "    bool retvalue = true;\n"
            text_tmp += "    unsigned int i = 0;\n"
            if datatype.data_category == 'ARRAY':
                text_tmp += "    if(data1->current_size != data2->current_size){\n"
                text_tmp += "        return false;\n"
                text_tmp += "    }\n\n"
                text_tmp += "    for (i=0; i<data1->current_size; i++){\n"
                text_tmp += _generate_compare_if(libraries, next_datatype, "        ", "data1->data[i]", "data2->data[i]")
            else:
                text_tmp += "    for (i=0; i<"+fix_C_libname(datatype.lib_name)+"__"+datatype.name+"_MAXSIZE; i++){\n"
                text_tmp += _generate_compare_if(libraries, next_datatype, "        ", "(*data1)[i]", "(*data2)[i]")
            text_tmp += "        {\n"
            text_tmp += "            retvalue = false;\n"
            text_tmp += "            break;\n"
            text_tmp += "        }\n"
            text_tmp += "    }\n"
            text_tmp += "    return retvalue;\n"

        elif datatype.data_category in ['RECORD', 'VARIANT_RECORD']:
            if datatype.data_category == 'VARIANT_RECORD':
                selector_name = datatype.selector["name"]
                selector_type = _find_dtype(datatype.selector["type_name"], libraries)

                text_tmp += "    if (data1->"+selector_name+" != data2->"+selector_name+"){\n"
                text_tmp += "        return false;\n"
                text_tmp += "    }\n"
                text_tmp += "    switch(data1->"+selector_name+"){\n"

                for union in datatype.union_list:
                    union_type = _find_dtype(union["type_name"], libraries)
                    value = _find_selector_value(lib, union["when"], selector_type)

                    text_tmp += "    case "+value+":\n"
                    text_tmp += _generate_compare_if(libraries, union_type, "        ", "data1->u_"+selector_name+"."+union["name"], "data2->u_"+selector_name+"."+union["name"])
                    text_tmp += "        {\n"
                    text_tmp += "            return false;\n"
                    text_tmp += "        }\n"
                    text_tmp += "        break;\n"

                text_tmp += "    default:\n"
                text_tmp += "        return false;\n"
                text_tmp += "    }\n"

            for field in datatype.field_list:
                field_type = _find_dtype(field["type_name"], libraries)
                text_tmp += _generate_compare_if(libraries, field_type, "    ", "data1->"+field["name"], "data2->"+field["name"])
                text_tmp += "        {\n"
                text_tmp += "                return false;\n"
                text_tmp += "        }\n"
            text_tmp+="    return true;\n"

        else:
            text_tmp+="return false;"

        text_tmp += "}\n\n"

        text+=_add_64BIT_macro_protection(lib, datatype, text_tmp)

    return text
