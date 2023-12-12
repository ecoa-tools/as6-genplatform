# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

import os
import subprocess
import re
from xml.etree import ElementTree
from collections import OrderedDict
from ecoa.utilities.logs import error, info

from ecoa.utilities.namespaces import ECOS_BIN
from ecoa.utilities.xml_utils import write_xml_file

def __generate_c_function(module_impl, module_type):
    string_file="\
#include <stdio.h>\n\
#include \"ECOA.h\"\n\
#include \"#MODULE_NAME#_user_context.h\"\n\
int main(void){\n\
    #USER_CTX#\n\
    #WARM_CTX#\n\
    return 0;\n\
}\n"

    string_user_ctx = "printf(\"Size of #MODULE_NAME#_user_context: %i\\n\", sizeof(#MODULE_NAME#_user_context));"
    string_warm_ctx = "printf(\"Size of #MODULE_NAME#_warm_start_context: %i\\n\\n\", sizeof(#MODULE_NAME#_warm_start_context));"
    string_no_user_ctx = "printf(\"Size of #MODULE_NAME#_user_context: 0\\n\");"
    string_no_warm_ctx = "printf(\"Size of #MODULE_NAME#_warm_start_context: 0\\n\\n\");"

    if module_type.user_context:
        string_file = string_file.replace("#USER_CTX#", string_user_ctx)
    else:
        string_file = string_file.replace("#USER_CTX#", string_no_user_ctx)

    if module_type.warm_start_context:
        string_file = string_file.replace("#WARM_CTX#", string_warm_ctx)
    else:
        string_file = string_file.replace("#WARM_CTX#", string_no_warm_ctx)

    return string_file.replace("#MODULE_NAME#", module_impl.name)

def __generate_cpp_function(module_impl, module_type):
    string_file="\
#include <stdio.h>\n\
#include \"ECOA.hpp\"\n\
#include \"#MODULE_NAME#_user_context.hpp\"\n\
#if defined(__cplusplus)\n\
extern \"C\" {\n\
#endif\n\
int main(void){\n\
    #USER_CTX#\n\
    #WARM_CTX#\n\
    return 0;\n\
}\n\
#if defined(__cplusplus)\n\
}\n\
#endif\n"

    string_user_ctx = "printf(\"Size of #MODULE_NAME#_user_context: %i\\n\", sizeof(#MODULE_NAME#::user_context));"
    string_warm_ctx = "printf(\"Size of #MODULE_NAME#_warm_start_context: %i\\n\\n\", sizeof(#MODULE_NAME#::warm_start_context));"
    string_no_user_ctx = "printf(\"Size of #MODULE_NAME#_user_context: 0\\n\");"
    string_no_warm_ctx = "printf(\"Size of #MODULE_NAME#_warm_start_context: 0\\n\\n\");"


    if module_type.user_context:
        string_file = string_file.replace("#USER_CTX#", string_user_ctx)
    else:
        string_file = string_file.replace("#USER_CTX#", string_no_user_ctx)

    if module_type.warm_start_context:
        string_file = string_file.replace("#WARM_CTX#", string_warm_ctx)
    else:
        string_file = string_file.replace("#WARM_CTX#", string_no_warm_ctx)

    return string_file.replace("#MODULE_NAME#", module_impl.name)


def __find_context_size(module_impl, module_type, comp_dir, lib_directory,
                        c_compiler, cpp_compiler, c_flags, cpp_flags):
    """find the user context and warm start context sizes of a module implementation.

    Attributes:
        module_impl   (Module_Implementation): The module implementation
        module_type             (Module_Type): The module type
        comp_dir      (str): The component implementation directory (where modules are generated)
        lib_directory (str): The library directory 0-Types
        c_compiler    (str): The c compiler
        cpp_compiler  (str): The cpp compiler
        c_flags       (str): The c flags
        cpp_flags     (str): The cpp flags

    Return:
        (str,str): size of user context, size of warm start context
    """
    module_ctx_dir = os.path.join(comp_dir, module_impl.name, "inc")
    c_filename = os.path.join(comp_dir, "test", module_impl.name+"_cxt_size.c")

    # create dir if necessary:
    os.makedirs(os.path.dirname(c_filename), exist_ok=True)

    # create C file
    if module_impl.language == "C++":
        fct_str = __generate_cpp_function(module_impl, module_type)
    else:
        fct_str = __generate_c_function(module_impl, module_type)
    c_file = open(c_filename, "w")
    c_file.write(fct_str)
    c_file.close()

    # compile commande line:
    lib_includes = [module_ctx_dir,
                    os.path.join(comp_dir, module_impl.name, "inc-gen"),
                    os.path.join(lib_directory, "inc-gen")]

    cmd_compile_line = "#COMPILER# #FLAGS# -I %s %s -o %s/compute_ctx_size" % \
                (' -I '.join(map(str,lib_includes)),
                 c_filename,
                 os.path.dirname(c_filename))
    if module_impl.language == "C++":
        cmd_compile_line = cmd_compile_line.replace("#COMPILER#", cpp_compiler)\
                                           .replace("#FLAGS#", cpp_flags)
    else:
        cmd_compile_line = cmd_compile_line.replace("#COMPILER#", c_compiler)\
                                           .replace("#FLAGS#", c_flags)

    # run compilation command:
    process = subprocess.Popen(cmd_compile_line, shell=True, stderr=subprocess.PIPE)
    output, stderr =process.communicate()
    if process.returncode != 0:
        error("An error occured during compilation of '%s'. "%(c_filename)+
              "Impossible to compute sizes of user_context and warm_start_contex of module '%s'."%module_impl.name)
        print(cmd_compile_line)
        print(stderr.decode('utf8'))
        return "0", "0"

    # run executable to compute sizes:
    cmd_run_line = os.path.dirname(c_filename)+"/compute_ctx_size"
    process = subprocess.Popen(cmd_run_line, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, stderr = process.communicate()
    if process.returncode != 0:
        error("An error occured during execution of '%s'. "%(cmd_run_line)+
              "Impossible to compute sizes of user_context and warm_start_contex of module '%s'."%module_impl.name)
        return "0", "0"

    # extract sizes from output:
    regex = r"^.*:\s([0-9]+)"
    matches = re.findall(regex, output.decode('utf8'), re.MULTILINE)
    if len(matches) != 2:
        return "0", "0"
    else:
        user_ctx_size, warm_ctx_size = matches
        return user_ctx_size, warm_ctx_size

def __generate_bin_desc(comp_impl, context_sizes_dict):
    """Generate the XML tree of a binary description file

    Attributes:
        comp_impl          ():The component implementation
        context_sizes_dict ():The context sizes dictionary of each module

    Return:
        (ElementTree) :XML tree
    """
    ElementTree.register_namespace("", ECOS_BIN[1:-1])
    root = ElementTree.Element(ECOS_BIN+"binDesc", attrib={"componentImplementation":comp_impl.name})

    ElementTree.SubElement(root, "processorTarget", attrib={"type":"x86_64"})

    for module_impl_name in comp_impl.module_implementations.keys():
        context_size, warm_context_size = context_sizes_dict[module_impl_name]
        ElementTree.SubElement(root, "binaryModule", attrib={
                "reference" : module_impl_name,
                "object" : "bin/%s.o"%module_impl_name,
                "checksum" : "0",
                "heapSize" : "10000",
                "stackSize" : "100000" ,
                "userContextSize" : context_size,
                "warmStartContextSize" : warm_context_size,
            })
    return root


def binary_desc_generator(component_implementations, lib_directory,
                        c_compiler, cpp_compiler, c_flags, cpp_flags):

    info("binare_descriptor options:")
    info("C compiler cmd line  = %s %s"%(c_compiler, c_flags))
    info("Cpp compiler cmd line = %s %s"%(cpp_compiler, cpp_flags))

    for comp_impl,_ in component_implementations.values():
        # compute context size of each module implementations:
        module_inst__ctx_sizes = OrderedDict() #module_instance name => (user_ctx_size, warm_ctx_size)

        info("                                  +------------+------------+")
        info("   %30s | user ctx   |  warm ctx  |"%comp_impl.name)
        info(" +--------------------------------+------------+------------+")
        for module_impl in comp_impl.module_implementations.values():
            module_type = comp_impl.module_types[module_impl.type]
            user_ctx_size, warm_ctx_size =  __find_context_size(module_impl,
                                                                module_type,
                                                                comp_impl.impl_directory,
                                                                lib_directory,
                                                                c_compiler,
                                                                cpp_compiler,
                                                                c_flags,
                                                                cpp_flags)
            info(" | %30s | %10s | %10s |"%(module_impl.name, user_ctx_size, warm_ctx_size))
            module_inst__ctx_sizes[module_impl.name] = (user_ctx_size, warm_ctx_size)
        info(" +--------------------------------+------------+------------+")

        # generate bin-desc.xlm:
        root = __generate_bin_desc(comp_impl, module_inst__ctx_sizes)
        filename = os.path.join(comp_impl.impl_directory, "bin-desc.xml")
        write_xml_file(filename, root, force_write=False)

