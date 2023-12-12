# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

import os

from .encaps_C_headers_generator import generate_C_encaps_h
from .encaps_C_sources_generator import generate_C_encaps_c
from ecoa_genplatform.generators.force_generation import file_need_generation

def generate_C_encaps(module_impl, module_type, module_dir, prefix, force_flag, macro_dict):
    file_name_h = os.path.join(module_dir, "inc-gen", prefix+"_"+module_impl.name+".h" )
    file_name_c = os.path.join(module_dir, "src-gen", prefix+"_"+module_impl.name+".c" )
    if file_need_generation(file_name_h, force_flag):
        file_h = open(file_name_h, 'w')
        text = generate_C_encaps_h(module_impl, module_type, prefix, macro_dict)
        print(text, file=file_h)
        file_h.close()

    if file_need_generation(file_name_c, force_flag):
        file_c = open(file_name_c, 'w')
        text = generate_C_encaps_c(module_impl, module_type, prefix, macro_dict)
        print(text, file=file_c)
        file_c.close()
