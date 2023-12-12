# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

import os
from ecoa.utilities.logs import debug
from .C.types_compare_generator import generate_C_compare_types
from .C.types_zeroise_generator import generate_C_zeroise_types

def check_existing_dir(dir_path):
    if not os.path.exists(dir_path):
        debug("    Directory does not existed : %s" % (dir_path))
        os.makedirs(dir_path, exist_ok=True)

def generate_compare_types(directory, libraries, force_flag):
    """Generate compare functions for all libraries

    Args:
        directory   (str): types directory (where files will be created)
        libraries  (dict): dictionary of Libraries
        force_flag (bool): if True, files will be overwritten,
                           otherwise existing files will not be modifyed

    """
    if not os.path.exists(directory):
        debug("    Directory does not exist for %s" % (directory))

    check_existing_dir(directory + os.sep + "inc-gen")
    check_existing_dir(directory + os.sep + "src-gen")

    generate_C_compare_types(directory, libraries, force_flag);
    #@TODO generate_Cpp_compare_types(directory, libraries, force_flag);

def generate_zeroise_types(directory, libraries, force_flag):
    """Generate zeroise functions for all libraries

    Args:
        directory   (str): types directory (where files will be created)
        libraries  (dict): dictionary of Libraries
        force_flag (bool): if True, files will be overwritten,
                           otherwise, existing files will not be modifyed

    """
    if not os.path.exists(directory):
        debug("    Directory does not exist for %s" % (directory))

    check_existing_dir(directory + os.sep + "inc-gen")
    check_existing_dir(directory + os.sep + "src-gen")

    generate_C_zeroise_types(directory, libraries, force_flag)
    #@TODO generate_Cpp_zeoise_types(directory, libraries, force_flag)
