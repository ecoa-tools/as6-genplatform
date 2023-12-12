# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

import os
from ecoa.utilities.logs import debug, info

def file_need_generation(file_path, force_flag, message=None):
    need_generation = True
    if message:
      l_message = message
    else:
      l_message = "    file already exists (%s)" % file_path

    if os.path.exists(file_path):
        debug(l_message)
        need_generation = False
        if force_flag:
            info("    Erase existing implementation (%s)" % file_path)
            os.remove(file_path)
            need_generation = True

    return need_generation

