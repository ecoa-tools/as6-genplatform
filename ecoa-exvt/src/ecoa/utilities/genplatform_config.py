# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

""" genplatform_config module """
from xml.etree.ElementTree import ElementTree
import os

from ..utilities.namespaces import NameSpaces, PARSEC_CONFIG
from ..utilities.logs import critical

def parse_config(filename, cl_composite, working_directory=""):
    """ Parse genplatform config file """

    if os.path.exists(filename) is False:
        critical("Configuration file %s does not exist" % (filename))
        return ("noname", "noname", "noname", "noname", "noname", "noname", "noname")

    # XML parsing using xml.etree module
    ns = NameSpaces()
    ns.setup_parsing()
    tree = ElementTree()
    tree.parse(filename)

    composite_filename = ""
    types_directory = ""
    implementation_directory = ""
    service_directory = ""
    component_directory = ""
    deployment_filename = ""
    integration_directory =""

    for element in tree.iterfind(PARSEC_CONFIG + "composite"):
        composite_filename = element.get("filename")

    for element in tree.iterfind(PARSEC_CONFIG + "types"):
        types_directory = element.get("directory")

    for element in tree.iterfind(PARSEC_CONFIG + "component_implementations"):
        implementation_directory = element.get("directory")

    for element in tree.iterfind(PARSEC_CONFIG + "components"):
        component_directory = element.get("directory")

    for element in tree.iterfind(PARSEC_CONFIG + "services"):
        service_directory = element.get("directory")

    for element in tree.iterfind(PARSEC_CONFIG + "deployment"):
        deployment_filename = element.get("filename")

    for element in tree.iterfind(PARSEC_CONFIG + "integration"):
        integration_directory = element.get("directory")

    if cl_composite != "":
        composite_filename = cl_composite

    return (working_directory+composite_filename,
            working_directory+types_directory,
            working_directory+implementation_directory,
            working_directory+component_directory,
            working_directory+service_directory,
            working_directory+deployment_filename,
            working_directory+integration_directory)
