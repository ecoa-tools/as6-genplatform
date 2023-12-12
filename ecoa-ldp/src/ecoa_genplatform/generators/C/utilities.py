# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

def expand_data_type(dtype):
    """@TODO Function docstring"""
    if dtype in  ('char8', 'boolean8', 'byte',
                  'int8', 'int16', 'int32', 'int64',
                  'uint8', 'uint16', 'uint32', 'uint64',
                  'float32', 'double64'):
        expanded_data_type = 'ECOA__' + dtype
    else:
        expanded_data_type = str.replace(dtype, ':', '__')
    return expanded_data_type
