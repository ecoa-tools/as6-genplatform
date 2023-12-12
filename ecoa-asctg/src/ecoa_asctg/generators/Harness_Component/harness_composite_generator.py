# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

from xml.etree import ElementTree

from ecoa.utilities.logs import info
from ecoa.utilities.namespaces import CSA, ECOS_CSA
from .harness_utils import write_xml_file

def update_composite_file(global_config, harness_type_comp_name, harness_comp_name, harness_comp,
                            keep_wires, new_wires, new_services, new_references, composite_file):
    composite_xml_tree = ElementTree.parse(composite_file)

    ElementTree.register_namespace("csa", CSA[1:-1])
    ElementTree.register_namespace("ecoa-sca", ECOS_CSA[1:-1])

    composite_root = composite_xml_tree.getroot()

    # remove components replaced by HARNESS
    for c_comp in composite_root.findall(CSA+"component"):
        # using root.findall() to avoid removal during traversal
        if c_comp.attrib['name'] not in harness_comp:
            composite_root.remove(c_comp)

    # remove all wires
    for c_wire in composite_root.findall(CSA+"wire"):
        # using root.findall() to avoid removal during traversal
        composite_root.remove(c_wire)

    # new component (only if necessary)
    if composite_root.find(CSA+"component[@name='%s']" % harness_comp_name) is None:
        new_comp_node = ElementTree.Element(CSA+"component", attrib={"name": "%s" % harness_comp_name})
        composite_root.insert(0, new_comp_node)
        new_inst_comp_node = ElementTree.SubElement(new_comp_node, ECOS_CSA+"instance",
                                                    attrib={"componentType": harness_type_comp_name})
        ElementTree.SubElement(new_inst_comp_node, ECOS_CSA+"implementation", attrib={"name": harness_comp_name})
        for service_name in new_services.keys():
            ElementTree.SubElement(new_comp_node, CSA+"service", attrib={"name": service_name})

        for ref_name in new_references.keys():
            ElementTree.SubElement(new_comp_node, CSA+"reference", attrib={"name": ref_name})

    # new wires
    composite_root.append(ElementTree.Comment("New wires with HARNESS component:"))
    for w in keep_wires + new_wires:
        ElementTree.SubElement(composite_root, CSA+"wire", attrib={"source": w.source_component+"/"+w.source_service,
                                                                   "target": w.target_component+"/"+w.target_service})

    write_xml_file(global_config, global_config.m_harness_composite_filename, composite_root)
    info("Composite File '%s' has been updated" % global_config.m_harness_composite_filename)


