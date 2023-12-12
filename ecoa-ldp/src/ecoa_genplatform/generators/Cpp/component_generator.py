# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

import codecs
import jinja2
from collections import OrderedDict
from ..C.driver_api_generator import os
from ..C.component_generator import generate_module_start_fct
from ..C.operation_generator import generate_params_variable, generate_param_fct_call2, \
    generate_temporary_complex_params_variable, generate_temporary_param_fct_call2
from ecoa.utilities.logs import debug
from ..fix_names import fix_Cpp_lib_filename, fix_C_data_type
from ..version_header_generator import generate_ldp_version_header_warning
from .operation_generator import generate_param_fct_call_cpp, generate_params_variable_cpp, fix_Cpp_data_type
from ..force_generation import file_need_generation

# from models import component_implementation
template_dir=os.path.dirname(os.path.abspath(__file__))+os.sep+'templates'
fsloader = jinja2.FileSystemLoader(template_dir)
env = jinja2.Environment(loader=fsloader, extensions=['jinja2.ext.do'])
#remove excessive blank lines
env.trim_blocks = True
env.lstrip_blocks = True

##################################
def generate_component_hpp(impl_dir, comp_list, component_impl, force_flag):
    c_filename = impl_dir + os.sep + "component_" + component_impl.get_name() + ".hpp"
    if not file_need_generation(c_filename,
                            force_flag,
                            "Component H file already exists for " + component_impl.get_name()):
        return

    template = env.get_template('template_component_compname.hpp.jj')

    rt=template.render(component_impl = component_impl, comp_list = comp_list)

    ofh=codecs.open(c_filename,"w", encoding="utf-8")
    ofh.write(generate_ldp_version_header_warning())
    ofh.write(rt)
    ofh.close()

##################################
def generate_component_cpp(impl_dir, comp_list, component_type, component_impl, wires, force_flag, libraries,
                           protection_domains, components, component_implementations):
    first_op_async_dict = OrderedDict()
    for module_i in component_impl.get_module_instances():
        module_impl = component_impl.get_module_implementations()[module_i.get_implementation()]
        mtype = component_impl.get_module_type(module_impl.type)
        first_op_async_dict[module_i] = next((op for op in mtype.operations.values() if op.type == 'ARS'), None)

    c_filename = impl_dir + os.sep + "component_" + component_impl.get_name() + ".cpp"
    if not file_need_generation(c_filename,
                            force_flag,
                            "Component C file already exists for " + component_impl.get_name()):
        return

    template = env.get_template('template_component_compname.cpp.jj')

    rt=template.render(comp_list=comp_list, component_impl = component_impl, libraries=libraries,
                       first_op_async_dict=first_op_async_dict,
                       generate_param_fct_call_cpp = generate_param_fct_call_cpp,
                       enumerate=enumerate, str=str,
                       generate_params_variable_cpp = generate_params_variable_cpp,
                       fix_libname=fix_Cpp_lib_filename,
                       fix_data_type=fix_Cpp_data_type)
    ofh=codecs.open(c_filename,"w", encoding="utf-8")
    ofh.write(generate_ldp_version_header_warning())
    ofh.write(rt)
    ofh.close()

    # writes C modules
    fd = open(c_filename, 'a')

    print("extern \"C\" \n", file=fd)
    print("{",file=fd)

    for comp in comp_list:
        for module_i in component_impl.get_module_instances():
            module_impl = component_impl.get_module_implementations()[module_i.get_implementation()]
            if module_impl.language == "C":
                text = generate_module_start_fct(comp, component_impl, module_i, libraries, component_type, wires)
                print(text, file=fd)

    print("}",file=fd)
    fd.close()

