# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

import os
from xml.etree import ElementTree

from ecoa.utilities.logs import info
from ecoa.utilities.namespaces import ECOA_PROJECT
from .harness_utils import suffixed_harness_filename, write_xml_file


def update_project_config_file(global_config, platform_config_file):
    project_xml_tree = ElementTree.parse(platform_config_file)
    ElementTree.register_namespace("", ECOA_PROJECT[1:-1])
    project_root = project_xml_tree.getroot()

    componentDefinitions_node = project_root.find(ECOA_PROJECT+"componentDefinitions")
    componentImplementations_node = project_root.find(ECOA_PROJECT+"componentImplementations")
    implementationAssembly_node = project_root.find(ECOA_PROJECT+"implementationAssembly")
    implementationAssembly_node.text = suffixed_harness_filename(implementationAssembly_node.text)
    deploymentSchema_node = project_root.find(ECOA_PROJECT+"deploymentSchema")
    deploymentSchema_node.text = suffixed_harness_filename(deploymentSchema_node.text)

    # generate harness only if necessary:
    harness_generation = True
    relative_path_harness_type_file = os.path.relpath(global_config.m_harness_comp_type_file,
                                                      os.path.dirname(platform_config_file))
    relative_path_harness_impl_file = os.path.relpath(global_config.m_harness_comp_impl_file,
                                                      os.path.dirname(platform_config_file))
    for file_node in componentDefinitions_node.iterfind(ECOA_PROJECT+"file"):
        if file_node.text == relative_path_harness_type_file:
            harness_generation = False
    if harness_generation:
        componentDefinitions_node.append(ElementTree.Comment("New HARNESS component"))
        new_file_node = ElementTree.SubElement(componentDefinitions_node, "file")
        new_file_node.text = relative_path_harness_type_file

        componentImplementations_node.append(ElementTree.Comment("New HARNESS component implementation"))
        new_file_node2 = ElementTree.SubElement(componentImplementations_node, "file")
        new_file_node2.text = relative_path_harness_impl_file

    write_xml_file(global_config, global_config.m_harness_project_filename, project_root)
    info("Project config file '%s' has been updated" % global_config.m_harness_project_filename)


