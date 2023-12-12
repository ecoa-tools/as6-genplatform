# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

from ecoa.utilities.logs import debug
from ..fix_names import fix_Cpp_lib_filename, fix_Cpp_constant_value, fix_Cpp_data_type, fix_C_constant_value
from ..version_header_generator import generate_ldp_version_header_warning
from ..force_generation import file_need_generation

import os

#
# @TODO: Add code to insert XML comments within the headers
#
def generate_Cpp_types(directory,
                     libraries,
                     force_flag):
    if os.path.exists(directory) == False:
        debug("    Directory does not exist for %s" % (directory))
        return

    # test files
    if libraries["ECOA"][0].libfile_directory != "":
        ecoa_path = libraries["ECOA"][0].libfile_directory
    else:
        ecoa_path = directory
    test_directory = os.path.join(ecoa_path, "test")
    os.makedirs(test_directory, exist_ok=True)
    tf = test_directory + os.sep + "serialization_test.cpp"
    if file_need_generation(tf,
                            force_flag,
                            "    C++ generated test already exists for %s" % tf):
        td = open(tf, 'w')
        print(generate_ldp_version_header_warning(), file=td)
        print("#include <ECOA.hpp>", file=td)
        for ln, li in libraries.items():
            if ln == 'ECOA':
                continue
            print("#include \"" + fix_Cpp_lib_filename(ln) + ".hpp\"", file=td)
            print("#include \"" + ln + "_serialization.h\"", file=td)
            print("", file=td)
            print("int main(int argc, char **argv)", file=td)
            print("{", file=td)
            print("  return 0;", file=td)
            print("}", file=td)
        td.close()

    const_type_tpl = "\
/* Type #TYPE_NAME# #COMMENT# */\n\
#define #TYPE_NAME# (#VALUE#)\n"

    for ln, li in libraries.items():
        if ln == 'ECOA':
            continue

        header_directory = os.path.join(li[0].libfile_directory, "inc")
        os.makedirs(header_directory, exist_ok=True)

        lf = header_directory + os.sep + fix_Cpp_lib_filename(ln) + ".hpp"
        if file_need_generation(lf,
                                   force_flag,
                                   "    C header already exists for %s" % (lf)):

            fd = open(lf, 'w')


            print(generate_ldp_version_header_warning(), file=fd)
            print("/*", file=fd)
            print(" * @file "+ ln + ".hpp", file=fd)
            print(" * This is data-type declaration file", file=fd)
            print(" */", file=fd)
            print("", file=fd)

            print("",file=fd)
            print("#include \"ECOA.hpp\"\n",file=fd)
            for l in li[0].included_libs:
                print("#include \""+fix_Cpp_lib_filename(l)+".hpp\"", file=fd)


            print("#if !defined(_" + fix_Cpp_lib_filename(ln) + "_HPP)", file=fd)
            print("#define _" + fix_Cpp_lib_filename(ln) + "_HPP", file=fd)

            print("#if defined(__cplusplus)", file=fd)
            print("extern \"C\" {", file=fd)
            print("#endif /* __cplusplus */", file=fd)
            print("", file=fd)

            namespaces = ln.split(".")
            for ns in namespaces:
                print("namespace "+ns+"{", file=fd)
            print("",file=fd)


            for di in li[0].datatypes:
                cdn = di.name
                print("", file=fd)
                if di.data_category == 'SIMPLE':
                    data_type = fix_Cpp_data_type( di.data_type)
                    print("/* Type " + cdn + " " + di.comment + " */", file=fd)
                    print('typedef ' + data_type + ' ' + cdn + ';', file=fd)
                    minvalue = di.min_range
                    if minvalue != "":
                        minvalue = fix_Cpp_constant_value(minvalue)
                        print('static const ' + data_type + ' ' +  cdn + '_minRange = ' + minvalue + ";", file=fd)
                    maxvalue = di.max_range
                    if maxvalue != "":
                        maxvalue =  fix_Cpp_constant_value(maxvalue)
                        print('static const ' + data_type + ' ' +  cdn + '_maxRange = ' + maxvalue + ";", file=fd)

                elif di.data_category == 'CONSTANT':
                    data_type = fix_Cpp_data_type( di.data_type)
                    print("/* Constant " + cdn + " " + di.comment + " */", file=fd)
                    value = fix_Cpp_constant_value(di.value_str)
                    print('static const ' + data_type + ' ' + cdn + ' = ' + value + ';', file=fd)
                    print(const_type_tpl.replace("#TYPE_NAME#","__".join(namespaces) + '__' + cdn) \
                          .replace("#COMMENT#",di.comment)\
                                         .replace("#VALUE#",fix_C_constant_value(di.value_str)), file=fd)

                elif di.data_category == 'RECORD':
                    print("/* Type " + cdn + " */", file=fd)
                    print('typedef struct', file=fd)
                    print('{', file=fd)
                    for field in di.field_list:
                        field_string = '  ' + fix_Cpp_data_type( field["type_name"]) + ' ' + field["name"] + ';'
                        if field["comment"] != None:
                            field_string = field_string + ' /* ' + field["comment"] + ' */'
                        print(field_string, file=fd)
                    record_string = '} ' + cdn + ';'
                    if di.comment != "":
                        record_string = record_string + ' /* ' + di.comment + ' */'
                    print(record_string, file=fd)
                elif di.data_category == 'VARIANT_RECORD':
                    print("/* Type " + cdn + " */", file=fd)
                    print('typedef struct', file=fd)
                    print('{', file=fd)

                    selectorType =  fix_Cpp_data_type(di.selector["type_name"])
                    print("  " + selectorType + " " + di.selector["name"] + ";", file=fd)
                    for field in di.field_list:
                        field_string = '  ' + fix_Cpp_data_type( field["type_name"]) + ' ' + field["name"] + ';'
                        if field["comment"] != None:
                            field_string = field_string + ' /* ' + field["comment"] + ' */'
                        print(field_string, file=fd)

                    print('  union {', file=fd)
                    for union in di.union_list:
                        union_string = '  ' + fix_Cpp_data_type( union["type_name"]) + ' ' + union["name"] + ';'
                        if union["comment"] != None:
                            union_string = union_string + ' /* ' + union["comment"] + ' */'
                        print(union_string, file=fd)
                    print('  } u_' + di.selector["name"] + ';', file=fd)

                    record_string = '} ' + cdn + ';'
                    if di.comment != "":
                        record_string = record_string + ' /* ' + di.comment + ' */'
                    print(record_string, file=fd)
                elif di.data_category == 'ARRAY':
                    data_type = fix_Cpp_data_type( di.data_type)

                    print("/* Type " + cdn + " */", file=fd)
                    print("static const ECOA::uint32 " + cdn + "_MAXSIZE" + "=" +  fix_Cpp_constant_value(di.max_number) + ";", file=fd)
                    print("typedef struct {", file=fd)
                    print("  ECOA::uint32 current_size;", file=fd)
                    print("  " + data_type + " data[" + fix_C_constant_value(di.max_number) + "];", file=fd)
                    array_string = '} ' + cdn + ";"
                    if di.comment != "":
                        array_string += ' /* ' + di.comment + ' */'
                    print(array_string, file=fd)
                elif di.data_category == 'FIXED_ARRAY':
                    data_type = fix_Cpp_data_type( di.data_type)
                    print("/* Type " + cdn + " */", file=fd)
                    print("static const ECOA::uint32 " + cdn + "_MAXSIZE" + " =" + fix_Cpp_constant_value(di.max_number) + ";", file=fd)
                    array_string = "typedef " + data_type + ' ' + cdn + "[" + fix_C_constant_value(di.max_number) + "];"
                    if di.comment != "":
                        array_string += ' /* ' + di.comment + ' */'
                    print(array_string, file=fd)
                elif di.data_category == 'ENUM':
                    data_type = fix_Cpp_data_type( di.data_type)
                    print("/* Type " + cdn + " */", file=fd)
                    print('struct ' + cdn,file=fd)
                    print('{',file=fd)
                    print('   ' + data_type + ' value;',file=fd)
                    print('   enum EnumValues {',file=fd)
                    data_type = fix_Cpp_data_type( di.data_type)

                    di.evaluate_empty_value(libraries)
                    for enum in di.enum_list:
                        enum_val2 = fix_C_constant_value(enum["value"])
                        print('   '+ enum["name"] + ' = ' + str(enum_val2) + ', /*' + enum["comment"] + '*/' , file= fd)

                    print('    };',file=fd)
                    print('    inline void operator = (' + data_type + ' i) {value = i; }',file=fd)
                    print('    inline explicit operator ' + data_type + '() const { return value; }',file=fd)
                    print('    inline explicit '+cdn+'(EnumValues v):value(v) {}',file=fd)
                    print('    inline '+cdn+'():value('+di.enum_list[0]["name"]+') {}',file=fd)
                    print('};',file=fd)


                else:
                    print('unknown category type %s for %s' % (di.data_category, di.get_name()))

            print("", file=fd)
            # print("} /* namespace */ \n",file=fd)
            for ns in reversed(namespaces):
                print("} /* "+ns+" */ ", file=fd)
            print("#if defined(__cplusplus)", file=fd)
            print("}", file=fd)
            print("#endif /* __cplusplus */", file=fd)
            print("", file=fd)
            print("#endif /* _" + fix_Cpp_lib_filename(ln) + "_HPP */", file=fd)

            fd.close()
