# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

import codecs
import jinja2
import os
from .operation_generator import generate_header_fct_cpp
from ecoa.utilities.logs import debug
from ..fix_names import fix_Cpp_lib_filename
from ..version_header_generator import generate_ldp_version_header, generate_ldp_version_header_warning
from ..force_generation import file_need_generation

template_dir=os.path.dirname(os.path.abspath(__file__))+os.sep+'templates'
fsloader = jinja2.FileSystemLoader(template_dir) #dossier ou se trouvent les template
env = jinja2.Environment(loader=fsloader)
env.trim_blocks = True
env.lstrip_blocks = True



def generate_Cpp_module(directory, mimpl, mtype, libraries, force_flag):
    c_filename = os.path.join(directory, mimpl.get_name() + '.cpp')

    if file_need_generation(c_filename,
                            force_flag,
                            "module C implementation already exists for " + mimpl.get_name()):

        template = env.get_template('template_mname_module.cpp.jj') #nomdutemplate
        mname = mimpl.get_name()

        rt=template.render(mname=mname, libraries=libraries,mtype=mtype,
                           generate_header_fct_cpp=generate_header_fct_cpp,
                           fix_libname=fix_Cpp_lib_filename)

        ofh=codecs.open(c_filename,"w", encoding="utf-8")
        ofh.write(generate_ldp_version_header())
        ofh.write(rt)
        ofh.close()



def generate_Hpp_user_context(directory, mimpl, mtype, libraries, force_flag):
    h_filename = os.path.join(directory, mimpl.get_name() + '_user_context.hpp')

    if file_need_generation(h_filename,
                            force_flag,
                            "A module header user_context already exists for " + mimpl.get_name()):

        template = env.get_template('template_mname_user_context.hpp.jj') #nomdutemplate
        mname = mimpl.get_name()

        rt = template.render(mname=mname,libraries=libraries,mtype=mtype,
                             fix_libname=fix_Cpp_lib_filename)

        ofh = codecs.open(h_filename,"w", encoding="utf-8")
        ofh.write(generate_ldp_version_header())
        ofh.write(rt)
        ofh.close()


def generate_Hpp_module(directory, mimpl, mtype, libraries, force_flag):
    h_filename = os.path.join(directory, mimpl.get_name() + '.hpp')

    if not file_need_generation(h_filename,
                            force_flag,
                            "A module H file already exists for " + mimpl.get_name()):
        return

    template = env.get_template('template_mname_module.hpp.jj') #nomdutemplate

    mname = mimpl.get_name()
    rt=template.render(mname=mname, mimpl= mimpl, libraries=libraries,mtype=mtype,
                       generate_header_fct_cpp=generate_header_fct_cpp,
                       fix_libname=fix_Cpp_lib_filename)

    ofh=codecs.open(h_filename,"w", encoding="utf-8")
    ofh.write(generate_ldp_version_header_warning())
    ofh.write(rt)
    ofh.close()
