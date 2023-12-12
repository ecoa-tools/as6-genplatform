# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

# JinjaTest1.py is an attempt to write a module that exploits Jinja templates.

# the current file is *not* a template

import codecs
import jinja2
import os
from .operation_generator import generate_header_fct_cpp, generate_broadcast_event_send_cpp,\
    generate_async_request_send_cpp, generate_sync_request_send_cpp, generate_response_send_cpp
from ..C.properties_generator import property_get_function_generate_cpp
from ecoa.utilities.logs import debug
from ..fix_names import fix_Cpp_lib_filename, fix_Cpp_data_type
from ..version_header_generator import generate_ldp_version_header_warning
from ..force_generation import file_need_generation

template_dir=os.path.dirname(os.path.abspath(__file__))+os.sep+'templates'
fsloader = jinja2.FileSystemLoader(template_dir)

env = jinja2.Environment(loader=fsloader)
env.trim_blocks = True
env.lstrip_blocks = True

def generate_Cpp_container(directory, mimpl, mtype, libraries,comp_impl_name,
                         force_flag):
    c_filename = os.path.join(directory, mimpl.get_name() + '_container.cpp')

    if not file_need_generation(c_filename,
                            force_flag,
                            "A module container already exists for " + mimpl.get_name()):
        return

    template = env.get_template('template_mname_module_container.cpp.jj')
    mname = mimpl.get_name()

    rt=template.render(mname=mname, mtype=mtype, comp_impl_name=comp_impl_name, libraries=libraries,
                       generate_header_fct_cpp=generate_header_fct_cpp,
                       property_get_function_generate_cpp=property_get_function_generate_cpp,
                       enumerate=enumerate,
                       str=str,
                       fix_libname=fix_Cpp_lib_filename,
                       generate_broadcast_event_send_cpp=generate_broadcast_event_send_cpp,
                       generate_async_request_send_cpp=generate_async_request_send_cpp,
                       generate_sync_request_send_cpp=generate_sync_request_send_cpp,
                       generate_response_send_cpp=generate_response_send_cpp)

    ofh=codecs.open(c_filename,"w", encoding="utf-8")
    ofh.write(generate_ldp_version_header_warning())
    ofh.write(rt)
    ofh.close()


def generate_Hpp_container_types(directory, mimpl, mtype, libraries,
                         force_flag):
    h_filename = os.path.join(directory, mimpl.get_name() + '_container_types.hpp')

    if not file_need_generation(h_filename,
                            force_flag,
                            "A module container header already exists " + mimpl.get_name()):
        return

    template = env.get_template('template_mname_module_container_types.hpp.jj')
    mname = mimpl.get_name()

    rt=template.render(mname=mname, mtype = mtype, fix_Cpp_data_type=fix_Cpp_data_type)


    ofh=codecs.open(h_filename,"w", encoding="utf-8")
    ofh.write(generate_ldp_version_header_warning())
    ofh.write(rt)
    ofh.close()

def generate_Hpp_container(directory, mimpl, mtype, libraries,
                         force_flag):
    h_filename = os.path.join(directory, mimpl.get_name() + '_container.hpp')

    if not file_need_generation(h_filename,
                            force_flag,
                            "A module container header already exists " + mimpl.get_name()):
        return

    template = env.get_template('template_mname_module_container.hpp.jj')
    mname = mimpl.get_name()

    rt=template.render(mname=mname,mimpl=mimpl,mtype=mtype,libraries=libraries,
                       generate_header_fct_cpp=generate_header_fct_cpp, str=str,
                       fix_libname=fix_Cpp_lib_filename, fix_Cpp_data_type=fix_Cpp_data_type)

    ofh=codecs.open(h_filename,"w", encoding="utf-8")
    ofh.write(generate_ldp_version_header_warning())
    ofh.write(rt)
    ofh.close()
