# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

def fix_C_data_type(dtype):
    return dtype.replace(':','__').replace('.','__')

def fix_C_constant_value(value):
    if value[0]=='%':
        return value.replace('%', '').replace(':','__').replace('.','__')
    else:
        return value

def fix_C_libname(libname):
  return libname.replace('.','__')


def fix_Cpp_data_type(dtype):
    return dtype.replace(':','::').replace('.','::')

def fix_Cpp_constant_value(value):
    if value[0]=='%':
        return value.replace('%', '').replace(':','::').replace('.','::')
    else:
        return value

def fix_Cpp_lib_filename(libname):
  return libname.replace('.','__')
