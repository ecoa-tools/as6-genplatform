# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

import os
import shutil
import sys
from ecoa.utilities.logs import debug, error
from ..fix_names import fix_C_data_type, fix_C_constant_value, fix_C_libname
from ..version_header_generator import generate_ldp_version_header_warning
from ..force_generation import file_need_generation

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

def _find_dtype(datatype_name, libraries):
    lib_name, type_name = datatype_name.split(":")
    next_datatype = libraries[lib_name][0].datatypes2[type_name]
    return next_datatype

def _size_of_datatype(datatype_name, datatype_category):
    if datatype_category in ['SIMPLE', 'CONSTANT', 'ENUM', "VARIANT_RECORD"]:
        return "sizeof(" + datatype_name + ")"
    elif datatype_category == "ARRAY":
        return "max_size_of_"+datatype_name +"()"
    else:
        return "size_of_" + datatype_name + "()"

def _current_size_of_datatype(datatype_name, datatype_category):
    if datatype_category in ['SIMPLE', 'CONSTANT', 'ENUM']:
        return "sizeof(" + datatype_name + ")"
    elif datatype_category in ["ARRAY", "VARIANT_RECORD"]:
        return "current_size_of_"+datatype_name +"(&(*data).data[i])"
    else:
        return "size_of_" + datatype_name + "()"

def _complex_char_of_datatype(datatype_category):
    if datatype_category in ['SIMPLE', 'CONSTANT', 'ENUM']:
        return ""
    else:
        return "&"

def generate_C_types(directory,
                     libraries,
                     force_flag):

    for ln, li in libraries.items():
        if ln == 'ECOA':
            continue
        header_directory = os.path.join(li[0].libfile_directory, "inc-gen")
        header_directory_ecoa = os.path.join(li[0].libfile_directory, "inc")
        impl_directory = os.path.join(li[0].libfile_directory, "src-gen")
        os.makedirs(header_directory, exist_ok=True)
        os.makedirs(impl_directory, exist_ok=True)

        generate_C_types_header(header_directory_ecoa, li[0], libraries, force_flag)
        generate_C_serialization_h(header_directory, li[0], force_flag)
        generate_C_serialization_c(impl_directory, li[0], libraries, force_flag)

    # test files
    if libraries["ECOA"][0].libfile_directory != "":
        ecoa_path = libraries["ECOA"][0].libfile_directory
    else:
        ecoa_path = directory
    test_directory = os.path.join(ecoa_path, "test")
    os.makedirs(test_directory, exist_ok=True)
    generate_C_type_serial_test(test_directory, libraries, force_flag)

    # Copy ECOA.h in the 0-Types/inc-gen directory
    cmodule = sys.modules['ecoa_genplatform.generators.C.types_generator']
    path = os.path.dirname(cmodule.__file__, )

    shutil.copy(path + os.sep + 'lib/ECOA.h', os.path.join(ecoa_path, "inc"))
    shutil.copy(path + os.sep + 'lib/ECOA.hpp', os.path.join(ecoa_path, "inc"))
    shutil.copy(path + os.sep + 'lib/ECOA_simple_types_serialization.h', os.path.join(ecoa_path, "inc-gen"))
    shutil.copy(path + os.sep + 'lib/ECOA_simple_types_serialization.c', os.path.join(ecoa_path, "src-gen"))





def generate_C_type_serial_test(test_directory, libraries, force_flag):
    # makefile test
    mf = test_directory + os.sep + "serialization_test.mak"
    if file_need_generation(mf,
                            force_flag,
                            "    Generated Makefile already exists %s" % mf):

        md = open(mf, 'w')
        print("all:", file=md)
        print("\tgcc -o serialization_test *.c -Wall -Werror -I ../inc-gen/ -I . "
              "-I $(ECOA_C_REPO) -DECOA_64BIT_SUPPORT",
              file=md)
        print("", file=md)
        print("clean:", file=md)
        print("\trm -f test", file=md)
        md.close()

    # main c test
    tf = test_directory + os.sep + "serialization_test.c"
    if file_need_generation(tf,
                            force_flag,
                            "    C generated test already exists %s" % tf):

        td = open(tf, 'w')
        print(generate_ldp_version_header_warning(), file=td)
        print("#include <ECOA.h>", file=td)
        for ln, li in libraries.items():
            if ln == 'ECOA':
                continue
            libname = fix_C_libname(ln)
            print("#include \"" + libname + ".h\"", file=td)
            print("#include \"" + libname + "_serialization.h\"", file=td)

        print("", file=td)
        print("int main(int argc, char **argv)", file=td)
        print("{", file=td)
        print("  return 0;", file=td)
        print("}", file=td)
        td.close()


def generate_C_types_header(header_directory, lib, libraries, force_flag):
    minRange_type_tpl="#define #TYPE_NAME#_minRange (#MINVALUE#)\n"
    maxRange_type_tpl="#define #TYPE_NAME#_maxRange (#MAXVALUE#)\n"
    const_type_tpl = "\
/* Type #TYPE_NAME# #COMMENT# */\n\
#define #TYPE_NAME# (#VALUE#)\n"
    simple_type_tpl="\
/* Type #TYPE_NAME# #COMMENT# */\n\
typedef #DATATYPE# #TYPE_NAME#;\n"


    libname = fix_C_libname(lib.name)

    lf = header_directory + os.sep + libname + ".h"
    if not file_need_generation(lf,
                            force_flag,
                            "    C header already exists %s" % (lf)):
        return

    fd = open(lf, 'w')
    print(generate_ldp_version_header_warning(), file=fd)
    print("/*", file=fd)
    print(" * @file " + libname + ".h", file=fd)
    print(" * This is data-type declaration file", file=fd)
    print(" * Generated by the function generate_C_types", file=fd)
    print(" */", file=fd)
    print("", file=fd)
    print("#if !defined(_" + libname + "_H)", file=fd)
    print("#define _" + libname + "_H", file=fd)
    print("#if defined(__cplusplus)", file=fd)
    print("extern \"C\" {", file=fd)
    print("#endif /* __cplusplus */", file=fd)
    print("", file=fd)

    for library in lib.included_libs:
        print("#include \"" + fix_C_libname(library) + ".h\"", file=fd)

    for di in lib.datatypes:
        cdn = libname + "__" + di.get_name()
        print("", file=fd)
        if di.data_category == 'SIMPLE':
            tmp_text = simple_type_tpl
            minvalue = di.min_range
            if minvalue != "":
                tmp_text += minRange_type_tpl.replace("#MINVALUE#", fix_C_constant_value(minvalue))
            maxvalue = di.max_range
            if maxvalue != "":
                tmp_text += maxRange_type_tpl.replace("#MAXVALUE#", fix_C_constant_value(maxvalue))

            tmp_text = tmp_text.replace("#TYPE_NAME#",cdn)\
                               .replace("#DATATYPE#", fix_C_data_type(di.data_type))\
                               .replace("#COMMENT#",di.comment)
            print(tmp_text, file=fd)

        elif di.data_category == 'CONSTANT':
            tmp_text = const_type_tpl.replace("#TYPE_NAME#",cdn)\
                                     .replace("#COMMENT#",di.comment)\
                                     .replace("#VALUE#",fix_C_constant_value(di.value_str))
            print(tmp_text, file=fd)
        elif di.data_category == 'RECORD':
            print("/* Type " + cdn + " */", file=fd)
            print('typedef struct', file=fd)
            print('{', file=fd)
            for field in di.field_list:
                field_string = '  ' + fix_C_data_type(field["type_name"]) + ' ' \
                                    + field["name"] + '; '
                if field['comment'] != None:
                    field_string += " /*" + field["comment"] +"*/"
                print(field_string, file=fd)
            record_string = '} ' + cdn + ';'
            if di.comment != "":
                record_string = record_string + ' /* ' + di.comment + ' */'
            print(record_string, file=fd)
        elif di.data_category == 'VARIANT_RECORD':
            print("/* Type " + cdn + " */", file=fd)
            print('typedef struct', file=fd)
            print('{', file=fd)
            print("  " + fix_C_data_type(di.selector["type_name"]) + " " + di.selector["name"] + ";", file=fd)

            for field in di.field_list:
                field_string = '  ' + fix_C_data_type(field["type_name"]) + ' ' \
                                    + field["name"] + ';'
                if field['comment'] != None:
                    field_string += " /*" + field["comment"] +"*/"
                print(field_string, file=fd)

            print('  union {', file=fd)
            for union_tuple in di.union_list:
                union_string = '  ' + fix_C_data_type(union_tuple["type_name"]) + ' ' \
                                     + union_tuple["name"] + ';'
                if union_tuple['comment'] != None:
                    union_string += " /*" + union_tuple["comment"] +"*/"
                print(union_string, file=fd)
            print('  } u_' + di.selector["name"] + ';', file=fd)

            record_string = '} ' + cdn + ';'
            if di.comment != "":
                record_string = record_string + ' /* ' + di.comment + ' */'
            print(record_string, file=fd)
        elif di.data_category == 'ARRAY':
            data_type = fix_C_data_type(di.data_type)
            print("/* Type " + cdn + " */", file=fd)
            print("#define " + cdn + "_MAXSIZE" + " (" + fix_C_constant_value(di.max_number) + ")", file=fd)
            print("typedef struct {", file=fd)
            print("  ECOA__uint32 current_size;", file=fd)
            print("  " + data_type + " data[" + cdn + "_MAXSIZE" + "];", file=fd)
            array_string = '} ' + cdn + ";"
            if di.comment != "":
                array_string += ' /* ' + di.comment + ' */'
            print(array_string, file=fd)

        elif di.data_category == 'FIXED_ARRAY':
            data_type = fix_C_data_type(di.data_type)
            print("/* Type " + cdn + " */", file=fd)
            print("#define " + cdn + "_MAXSIZE" + " (" + fix_C_constant_value(di.max_number) + ")", file=fd)
            array_string = "typedef " + data_type + ' ' + cdn + "[" + cdn + "_MAXSIZE" \
                           + "];"
            if di.comment != "":
                array_string += ' /* ' + di.comment + ' */'
            print(array_string, file=fd)
        elif di.data_category == 'ENUM':
            data_type = fix_C_data_type(di.data_type)
            print("/* Type " + cdn + " */", file=fd)
            print('typedef ' + data_type + ' ' + cdn + ';', file=fd)
            di.evaluate_empty_value(libraries)
            for enum in di.enum_list:
                enum_val2 = fix_C_constant_value(enum["value"])
                print('#define ' + cdn + '_' + enum["name"] + ' (' + str(enum_val2) + ')/*'
                      + enum["comment"] + '*/',
                      file=fd)
        else:
            error('Unknown category type %s for %s' % (di.data_category, di.get_name()))

    print("", file=fd)
    print("#if defined(__cplusplus)", file=fd)
    print("}", file=fd)
    print("#endif /* __cplusplus */", file=fd)
    print("", file=fd)
    print("#endif /* _" + libname + "_H */", file=fd)

    fd.close()



simple_serial_tpl_h="\
/* Type #DATATYPE_NAME# */\n\
void serialize_#DATATYPE_NAME#(const #DATATYPE_NAME# data, void *buffer, uint32_t max_size, uint32_t *added_size);\n\
void deserialize_#DATATYPE_NAME#(#DATATYPE_NAME# *data, void *buffer, uint32_t length);\n\
uint32_t size_of_#DATATYPE_NAME#(void);\n\n"

complex_serial_tpl_h="\
/* Type #DATATYPE_NAME# */\n\
void serialize_#DATATYPE_NAME#(const #DATATYPE_NAME#* data, void *buffer, uint32_t max_size, uint32_t *added_size);\n\
void deserialize_#DATATYPE_NAME#(#DATATYPE_NAME# *data, void *buffer, uint32_t length);\n\
uint32_t size_of_#DATATYPE_NAME#(void);\n\n"

constant_serial_tpl_H="\
/* Type #DATATYPE_NAME# */\n\
void serialize_#DATATYPE_NAME#(const #CST_DATATYPE_NAME# data, void *buffer, uint32_t max_size, uint32_t *added_size);\n\
void deserialize_#DATATYPE_NAME#(#CST_DATATYPE_NAME# *data, void *buffer, uint32_t length);\n\
uint32_t size_of_#DATATYPE_NAME#(void);\n\n"

array_serial_tpl_H="\
/* Type #DATATYPE_NAME# */\n\
void serialize_#DATATYPE_NAME#(const #DATATYPE_NAME#* data, void *buffer, uint32_t max_size, uint32_t *added_size);\n\
void deserialize_#DATATYPE_NAME#(#DATATYPE_NAME# *data, void *buffer, uint32_t length);\n\
uint32_t max_size_of_#DATATYPE_NAME#(void);\n\
uint32_t current_size_of_#DATATYPE_NAME#(const #DATATYPE_NAME# *data);\n\n"

var_record_serial_tpl_H="\
/* Type #DATATYPE_NAME# */\n\
void serialize_#DATATYPE_NAME#(const #DATATYPE_NAME#* data, void *buffer, uint32_t max_size, uint32_t *added_size);\n\
void deserialize_#DATATYPE_NAME#(#DATATYPE_NAME# *data, void *buffer, uint32_t length);\n\
uint32_t max_size_of_#DATATYPE_NAME#(#SELECTOR_TYPE# selector);\n\
uint32_t current_size_of_#DATATYPE_NAME#(const #DATATYPE_NAME# *data);\n\n"

def generate_C_serialization_h(test_directory, lib, force_flag):
    sln = fix_C_libname(lib.name)

    lshf = test_directory + os.sep + sln + "_serialization.h"
    if not file_need_generation(lshf,
                            force_flag,
                            "    C serialization header already exists for %s %s" % (sln, lshf)):
        return

    lshfd = open(lshf, 'w')
    print(generate_ldp_version_header_warning(), file=lshfd)
    print("/*", file=lshfd)
    print(" * @file " + sln + "_serialization.h", file=lshfd)
    print(" * This is data-type declaration file", file=lshfd)
    print(" */", file=lshfd)
    print("", file=lshfd)
    print("#if !defined(_" + sln + "_SERIALIZATION_H)", file=lshfd)
    print("#define _" + sln + "_SERIALIZATION_H", file=lshfd)
    print("#if defined(__cplusplus)", file=lshfd)
    print("extern \"C\" {", file=lshfd)
    print("#endif /* __cplusplus */", file=lshfd)
    print("", file=lshfd)
    print("#include <stdint.h>", file=lshfd)
    print("#include \"ECOA.h\"", file=lshfd)
    print("#include \"" + sln +".h\"", file=lshfd)
    for l in lib.included_libs:
        print("#include \"" + fix_C_libname(l) +".h\"", file=lshfd)

    print("", file=lshfd)

    text = ""
    for di in lib.datatypes:
        cdn = sln + "__" + di.get_name()
        if di.data_category in ['SIMPLE', 'ENUM']:
            text += simple_serial_tpl_h.replace("#DATATYPE_NAME#", cdn)
        elif di.data_category in ['RECORD', 'FIXED_ARRAY']:
            text += complex_serial_tpl_h.replace("#DATATYPE_NAME#", cdn)
        elif di.data_category == 'CONSTANT':
            data_type = fix_C_data_type(di.data_type)
            text += constant_serial_tpl_H.replace("#DATATYPE_NAME#", cdn)\
                                       .replace("#CST_DATATYPE_NAME#", data_type)
        elif di.data_category == 'ARRAY':
            text += array_serial_tpl_H.replace("#DATATYPE_NAME#", cdn)

        elif di.data_category == 'VARIANT_RECORD':
            text += var_record_serial_tpl_H.replace("#DATATYPE_NAME#", cdn)\
                                           .replace("#SELECTOR_TYPE#", fix_C_data_type(di.selector["type_name"]))

        else:
            error('unknown category type %s for %s' % (di.data_category, di.get_name()))

    print(text, file=lshfd)

    print("", file=lshfd)
    print("#if defined(__cplusplus)", file=lshfd)
    print("}", file=lshfd)
    print("#endif /* __cplusplus */", file=lshfd)
    print("", file=lshfd)
    print("#endif /* _" + sln + "_H */", file=lshfd)


    lshfd.close()

def _generate_fields_str(field_list, libraries, lib):
    serialized_fields_str=""
    deserialized_fields_str=""
    size_fields_str=""

    for field in field_list:
        category = lib.get_data_category(libraries, field["type_name"])
        fdt = fix_C_data_type(field["type_name"])
        fdn = field["name"]
        complex_char= _complex_char_of_datatype(category)
        fsize=_size_of_datatype(fdt, category)

        serialized_fields_str+="        max_field_size = "+fsize+";\n"
        serialized_fields_str+="        serialize_" + fdt + "("+complex_char+"(data->" + fdn + "), index, max_field_size, &added_field_size);\n"
        serialized_fields_str+="        index = index + added_field_size;\n"
        serialized_fields_str+="        added_field_size = 0;\n"

        deserialized_fields_str += "        field_size = "+fsize+";\n"
        deserialized_fields_str += "        deserialize_" + fdt + "(&(data->" + fdn + "), index, field_size);\n"
        deserialized_fields_str += "        index = index + "+fsize+";\n"

        size_fields_str += "    size = size + "+fsize+";\n"

    return serialized_fields_str, deserialized_fields_str, size_fields_str


def generate_C_serialization_c(directory, lib, libraries, force_flag):

    simple_tpl="\
/* Type #TYPE_NAME# */\n\
void serialize_#TYPE_NAME#(const #DATA_TYPE_NAME# data, void *buffer, uint32_t max_size, uint32_t *added_size)\n\
{\n\
    serialize_#NEXT_TYPE_NAME#((#NEXT_TYPE_NAME#)data, buffer, max_size, added_size);\n\
}\n\n\
void deserialize_#TYPE_NAME#(#DATA_TYPE_NAME# *data, void *buffer, uint32_t length)\n\
{\n\
    deserialize_#NEXT_TYPE_NAME#((#NEXT_TYPE_NAME# *)data, buffer, length);\n\
}\n\n\
uint32_t size_of_#TYPE_NAME#(void)\n\
{\n\
    return (uint32_t)sizeof(#DATA_TYPE_NAME#);\n\
}\n\n"

    array_tpl="\
/* Type #TYPE_NAME# */\n\
void serialize_#TYPE_NAME#(const #TYPE_NAME# *data, void *buffer, uint32_t max_size, uint32_t *added_size)\n\
{\n\
    uint32_t i = 0;\n\
    uint32_t item_added_size = 0;\n\
    void *index = buffer;\n\
    uint32_t item_size = 0;\n\
    if(max_size >= current_size_of_#TYPE_NAME#(data)) {\n\
        serialize_ECOA__uint32(data->current_size, index, sizeof(ECOA__uint32), &item_added_size);\n\
        index = index + item_added_size;\n\
        item_size = #NEXT_TYPE_SIZE#;\n\
        for(i = 0; i < data->current_size; i++) {\n\
            serialize_#NEXT_TYPE_NAME#(#COMPLEX_CHAR#(*data).data[i], index, item_size, &item_added_size);\n\
            index = index + item_added_size;\n\
            item_added_size = 0;\n\
        }\n\
        *added_size = current_size_of_#TYPE_NAME#(data);\n\
    }\n\
}\n\n\
void deserialize_#TYPE_NAME#(#TYPE_NAME# *data, void *buffer, uint32_t length)\n\
{\n\
    uint32_t i = 0;\n\
    void *index = buffer;\n\
    uint32_t item_size = 0;\n\
    if(length >= max_size_of_#TYPE_NAME#()) {\n\
        deserialize_ECOA__uint32(&data->current_size, index, sizeof(ECOA__uint32));\n\
        if(data->current_size > #TYPE_NAME#_MAXSIZE) {\n\
            data->current_size = #TYPE_NAME#_MAXSIZE;\n\
        }\n\
        index = index + sizeof(ECOA__uint32);\n\
        item_size = #NEXT_TYPE_SIZE#;\n\
        for(i = 0; i < data->current_size; i++) {\n\
            deserialize_#NEXT_TYPE_NAME#(&(*data).data[i], index, item_size);\n\
            index = index + #CURRENT_ITEM_SIZE#;\n\
        }\n\
    }\n\
}\n\n\
uint32_t max_size_of_#TYPE_NAME#(void)\n\
{\n\
    uint32_t size = 0;\n\
    size = #NEXT_TYPE_SIZE# * #TYPE_NAME#_MAXSIZE + sizeof(ECOA__uint32);\n\
    return size;\n\
}\n\n\
uint32_t current_size_of_#TYPE_NAME#(const #TYPE_NAME#*data)\n\
{\n\
    uint32_t size = 0;\n\
    size = #NEXT_TYPE_SIZE# * data->current_size + sizeof(ECOA__uint32);\n\
    return size;\n\
}\n\n"

    fixed_array_tpl="\
/* Type #TYPE_NAME# */\n\
void serialize_#TYPE_NAME#(const #TYPE_NAME# *data, void *buffer, uint32_t max_size, uint32_t *added_size)\n\
{\n\
    uint32_t i = 0;\n\
    uint32_t item_added_size = 0;\n\
    void *index = buffer;\n\
    uint32_t item_size = 0;\n\
    if(max_size >= size_of_#TYPE_NAME#()) {\n\
        item_size = #NEXT_TYPE_SIZE#;\n\
        for(i = 0; i < #TYPE_NAME#_MAXSIZE; i++) {\n\
            serialize_#NEXT_TYPE_NAME#(#COMPLEX_CHAR#(*data)[i], index, item_size, &item_added_size);\n\
            index = index + item_added_size;\n\
            item_added_size = 0;\n\
        }\n\
        *added_size = size_of_#TYPE_NAME#();\n\
    }\n\
}\n\n\
void deserialize_#TYPE_NAME#(#TYPE_NAME# *data, void *buffer, uint32_t length)\n\
{\n\
    uint32_t i = 0;\n\
    void *index = buffer;\n\
    uint32_t item_size = 0;\n\
    if(length >= size_of_#TYPE_NAME#()) {\n\
        item_size = #NEXT_TYPE_SIZE#;\n\
        for(i = 0; i < #TYPE_NAME#_MAXSIZE; i++) {\n\
            deserialize_#NEXT_TYPE_NAME#(&(*data)[i], index, item_size);\n\
            index = index + item_size;\n\
        }\n\
    }\n\
}\n\n\
uint32_t size_of_#TYPE_NAME#(void)\n\
{\n\
    uint32_t size = 0;\n\
    size = #NEXT_TYPE_SIZE# * #TYPE_NAME#_MAXSIZE;\n\
    return size;\n\
}\n\n"

    record_tpl="\
/* Type #TYPE_NAME# */\n\
void serialize_#TYPE_NAME#(const #TYPE_NAME# *data, void *buffer, uint32_t max_size, uint32_t *added_size)\n\
{\n\
    void *index = buffer;\n\
    uint32_t max_field_size = 0;\n\
    uint32_t added_field_size = 0;\n\
    if(max_size >= size_of_#TYPE_NAME#()) {\n\
#SERIALIZED_FIELDS#\n\
        *added_size = size_of_#TYPE_NAME#();\n\
    }\n\
}\n\n\
void deserialize_#TYPE_NAME#(#TYPE_NAME# *data, void *buffer, uint32_t length)\n\
{\n\
    void *index = buffer;\n\
    uint32_t field_size = 0;\n\
    if(length >= size_of_#TYPE_NAME#()) {\n\
#DESERIALIZED_FIELDS#\n\
    }\n\
}\n\n\
uint32_t size_of_#TYPE_NAME#(void)\n\
{\n\
    uint32_t size = 0;\n\
#SIZE_FIELDS#\n\
    return size;\n\
}\n"

    var_record_tpl="\
/* Type #TYPE_NAME# */\n\
void serialize_#TYPE_NAME#(const #TYPE_NAME# *data, void *buffer, uint32_t max_size, uint32_t *added_size)\n\
{\n\
    void *index = buffer;\n\
    uint32_t max_field_size = 0;\n\
    uint32_t added_field_size = 0;\n\
    if(max_size >= current_size_of_#TYPE_NAME#(data)) {\n\
        serialize_#SELECTOR_TYPE_NAME#(data->#SELECTOR_NAME#, index, sizeof(#SELECTOR_TYPE_NAME#), &added_field_size);\n\
        index = index + added_field_size;\n\
#SERIALIZED_FIELDS#\n\
        switch(data->#SELECTOR_NAME#){\n\
#SERIALIZED_UNIONS#\n\
        default:\n\
            break;\n\
        }\n\
        *added_size = current_size_of_#TYPE_NAME#(data);\n\
    }\n\
}\n\n\
void deserialize_#TYPE_NAME#(#TYPE_NAME# *data, void *buffer, uint32_t length)\n\
{\n\
    void *index = buffer;\n\
    uint32_t field_size = 0;\n\
    if(length >= max_size_of_#TYPE_NAME#(data->#SELECTOR_NAME#)) {\n\
        deserialize_#SELECTOR_TYPE_NAME#(&(data->#SELECTOR_NAME#), index, sizeof(#SELECTOR_TYPE_NAME#));\n\
        index = index + sizeof(#SELECTOR_TYPE_NAME#);\n\
#DESERIALIZED_FIELDS#\n\
        switch(data->#SELECTOR_NAME#){\n\
#DESERIALIZED_UNIONS#\n\
        default:\n\
            break;\n\
        }\n\
    }\n\
}\n\n\
uint32_t current_size_of_#TYPE_NAME#(const #TYPE_NAME# *data)\n\
{\n\
    return max_size_of_#TYPE_NAME#(data->#SELECTOR_NAME#);\n\
}\n\
\n\
uint32_t max_size_of_#TYPE_NAME#(#SELECTOR_TYPE_NAME# selector)\n\
{\n\
    uint32_t size = sizeof(#SELECTOR_TYPE_NAME#);\n\
#SIZE_FIELDS#\n\
    switch(selector){\n\
#SIZE_UNIONS#\n\
    default:\n\
        break;\n\
    }\n\
    return size;\n\
}\n"


    libname= fix_C_libname(lib.name)
    lscf = directory + os.sep + libname + "_serialization.c"

    if not file_need_generation(lscf,
                            force_flag,
                            "    C serialisation source already exists for %s %s" % (libname, lscf)):
        return

    lscfd = open(lscf, 'w')
    print(generate_ldp_version_header_warning(), file=lscfd)
    print("/*", file=lscfd)
    print(" * @file " + libname + "_serialization.c", file=lscfd)
    print(" * This is data-type declaration file", file=lscfd)
    print(" */", file=lscfd)
    print("#include <string.h>", file=lscfd)
    print("#include <stdint.h>", file=lscfd)
    print("#include <arpa/inet.h>", file=lscfd)
    print("#include <ECOA.h>", file=lscfd)
    print("#include <ECOA_simple_types_serialization.h>", file=lscfd)
    print("#include \"" + libname + ".h\"", file=lscfd)
    print("#include \"" + libname + "_serialization.h\"", file=lscfd)
    for library in lib.included_libs:
        print("#include \"" + fix_C_libname(library) + ".h\"", file=lscfd)
        print("#include \"" + fix_C_libname(library) + "_serialization.h\"", file=lscfd)


    print("", file=lscfd)

    for di in lib.datatypes:
        cdn = libname + "__" + di.get_name()
        print("", file=lscfd)
        if di.data_category == 'SIMPLE' or di.data_category == 'ENUM':
            data_type = fix_C_data_type(di.data_type)

            tmp_text = simple_tpl.replace("#TYPE_NAME#", cdn)\
                                 .replace("#DATA_TYPE_NAME#", cdn)\
                                 .replace("#NEXT_TYPE_NAME#", data_type)
            print(tmp_text, file=lscfd)

        elif di.data_category == 'CONSTANT':
            data_type = fix_C_data_type(di.data_type)
            value = fix_C_constant_value(di.value_str)

            tmp_text = simple_tpl.replace("#TYPE_NAME#", cdn)\
                                 .replace("#DATA_TYPE_NAME#", data_type)\
                                 .replace("#NEXT_TYPE_NAME#", data_type)
            print(tmp_text, file=lscfd)

        elif di.data_category == 'RECORD':
            tmp_text = record_tpl

            serialized_fields_str, \
            deserialized_fields_str, \
            size_fields_str = _generate_fields_str(di.field_list, libraries, lib)

            tmp_text = tmp_text.replace("#TYPE_NAME#", cdn)\
                               .replace("#SERIALIZED_FIELDS#", serialized_fields_str)\
                               .replace("#DESERIALIZED_FIELDS#", deserialized_fields_str)\
                               .replace("#SIZE_FIELDS#", size_fields_str)

            print(tmp_text, file = lscfd)

        elif di.data_category == 'VARIANT_RECORD':
            tmp_text = var_record_tpl

            serialized_fields_str, \
            deserialized_fields_str, \
            size_fields_str = _generate_fields_str(di.field_list, libraries, lib)

            #UNION FIELDS :
            selector_name = di.selector["name"]
            selector_type = _find_dtype(di.selector["type_name"], libraries)
            union_size_str        = ""
            union_serialize_str   = ""
            union_deserialize_str = ""

            for union in di.union_list:
                u_type = _find_dtype(union["type_name"], libraries)
                u_category = lib.get_data_category(libraries, union["type_name"])
                u_name = union["name"]
                u_type_str = fix_C_data_type(union["type_name"])
                value = _find_selector_value(lib, union["when"], selector_type)
                u_size = _size_of_datatype(u_type_str, u_category)
                complex_char= _complex_char_of_datatype(u_category)

                union_size_str += "case "+value+":\n"
                union_size_str += "    size = size + "+ u_size +";\n"
                union_size_str += "    break;\n"

                union_serialize_str += "case "+value+":\n"
                union_serialize_str += "    serialize_"+u_type_str+"("+complex_char+"(data->u_"+selector_name+"."+u_name+"), index, "+ u_size +", &added_field_size);\n"
                union_serialize_str += "    break;\n"


                union_deserialize_str += "case "+value+":\n"
                union_deserialize_str += "    deserialize_"+u_type_str+"(&(data->u_"+selector_name+"."+u_name+"), index, "+ u_size +");\n"
                union_deserialize_str += "    break;\n"

            tmp_text = tmp_text.replace("#TYPE_NAME#", cdn)\
                               .replace("#SERIALIZED_FIELDS#", serialized_fields_str)\
                               .replace("#DESERIALIZED_FIELDS#", deserialized_fields_str)\
                               .replace("#SIZE_FIELDS#", size_fields_str)\
                               .replace("#SELECTOR_TYPE_NAME#", fix_C_data_type(di.selector["type_name"]))\
                               .replace("#SELECTOR_NAME#", fix_C_data_type(di.selector["name"]))\
                               .replace("#SIZE_UNIONS#", union_size_str)\
                               .replace("#SERIALIZED_UNIONS#",union_serialize_str)\
                               .replace("#DESERIALIZED_UNIONS#",union_deserialize_str)

            print(tmp_text, file = lscfd)

        elif di.data_category == 'ARRAY':
            item_data_type = fix_C_data_type(di.data_type)
            item_category = lib.get_data_category(libraries, di.data_type)
            category_char = _complex_char_of_datatype(item_category)
            item_type_size =  _size_of_datatype(item_data_type, item_category)
            current_intem_size = _current_size_of_datatype(item_data_type, item_category)

            tmp_text = array_tpl.replace("#TYPE_NAME#", cdn)\
                                .replace("#NEXT_TYPE_NAME#", item_data_type)\
                                .replace("#COMPLEX_CHAR#", category_char)\
                                .replace("#NEXT_TYPE_SIZE#", item_type_size)\
                                .replace("#CURRENT_ITEM_SIZE#",current_intem_size)

            print(tmp_text, file=lscfd)

        elif di.data_category == 'FIXED_ARRAY':
            item_data_type = fix_C_data_type(di.data_type)
            item_category = lib.get_data_category(libraries, di.data_type)
            category_char = _complex_char_of_datatype(item_category)
            item_type_size =  _size_of_datatype(item_data_type, item_category)

            tmp_text = fixed_array_tpl.replace("#TYPE_NAME#", cdn)\
                                .replace("#NEXT_TYPE_NAME#", item_data_type)\
                                .replace("#COMPLEX_CHAR#", category_char)\
                                .replace("#NEXT_TYPE_SIZE#", item_type_size)
            print(tmp_text, file=lscfd)

        else:
            error('unknown category type %s for %s' % (di.data_category, di.get_name()))


    lscfd.close()

