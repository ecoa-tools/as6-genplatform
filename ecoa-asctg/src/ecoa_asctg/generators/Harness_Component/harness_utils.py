# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

import os
from ecoa.utilities.xml_utils import prettify


def get_harness_mod_str():
    return "MOD"


def get_module_type_name():
    return get_harness_mod_str() + "_HARNESS_mod_type"


def get_module_impl_name():
    return get_harness_mod_str() + "_HARNESS_mod_impl"


def get_module_inst_name():
    return get_harness_mod_str() + "_HARNESS_mod_inst"


def get_trigger_name():
    return get_harness_mod_str() + "_HARNESS_trigger"


def get_service_or_reference(services, references, service_name):
    if service_name in services:
        return "service"
    elif service_name in references:
        return "reference"
    return None


def get_harness_type_str():
    return "HARNESS_type"


def get_harness_str():
    return "HARNESS"


def suffixed_harness_filename(filename):
    l_path = os.path.split(filename)
    l_split = l_path[1].split('.')
    l_split[0] = l_split[0] + "-harness"
    l_filename = ".".join(l_split)
    return os.path.join(l_path[0], l_filename)


def write_xml_file(global_config, filename, xml_root):
    if global_config.ECOAProject.directory == global_config.ECOAProject.output_dir:
        l_filename = filename
    else:
        l_filename = os.path.join(global_config.ECOAProject.output_dir,
                                  os.path.relpath(filename, global_config.ECOAProject.directory))

    if os.path.dirname(l_filename) != "":
        os.makedirs(os.path.dirname(l_filename), exist_ok=True)

    f = open(l_filename, 'wb')
    f.write(prettify(xml_root))
    f.flush()
    f.close()
