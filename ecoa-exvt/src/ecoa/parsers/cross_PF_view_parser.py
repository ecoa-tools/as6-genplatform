# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

from xml.etree.ElementTree import ElementTree
from ..utilities.namespaces import ECOS_VIEW
from ..utilities.xml_utils import validate_XML_file
from ..utilities.logs import error, info, warning
from ..models.cross_PF_view import cross_platforms_view
from .euid_parser import parse_EUID_not_unique

import os

def parse_cross_PF_view(xsd_directory, filenames):
    if len(filenames) == 0:
        info("No cross platforms view")
        return cross_platforms_view("noName", "noName", "noName")

    filename = list(filenames)[0] # TODO what appends when there are many cross platforms view ?

    if not os.path.exists(filename):
        error("Cross platform view file '%s' doesn't exist"%(filename))
        return cross_platforms_view("noName", "noName", "noName")

    if validate_XML_file(filename, xsd_directory + "/Schemas_ecoa/ecoa-cross-platforms-view-2.0.xsd") == -1:
        return cross_platforms_view("noName", "noName", "noName")

    tree = ElementTree()
    tree.parse(filename)
    view_name = tree.getroot().get("name")
    view_assembly_name = tree.getroot().get("assembly")
    view_logical_system_name = tree.getroot().get("logicalSytem")
    cross_PF_view = cross_platforms_view(view_name, view_assembly_name, view_logical_system_name)

    for wire_map_node in tree.iterfind(ECOS_VIEW+"wireMapping"):
        pf_link_id = wire_map_node.get("mappedOnLinkId")
        (source_comp, source_serv) = wire_map_node.get("source").split('/')
        (target_comp, target_serv) = wire_map_node.get("target").split('/')
        cross_PF_view.add_wire_map(pf_link_id, source_comp, source_serv, target_comp, target_serv)

    for euid_node in tree.iterfind(ECOS_VIEW+"euidsBinding"):
        euids_file = euid_node.get("EUIDs")
        linkID = euid_node.get("boundToLinkId")

        euids_file = os.path.join(os.path.dirname(filename), euids_file+".ids.xml")
        cross_PF_view.add_euid_binding(euids_file, linkID)

        # parse euid Binding
        parse_EUID_not_unique(euids_file, cross_PF_view.EUIDs[euids_file])

    for composite_node in tree.iterfind(ECOS_VIEW + "composite"):
        comp_name = composite_node.get("name")
        dep_PF = composite_node.get("deployedOnComputingPlatform")
        cross_PF_view.composites_deployment[comp_name] = dep_PF

    return cross_PF_view


def check_cross_PF_view(cross_pf_view, platform_links, platforms, upper_composite):

    for pf_composite_name, pf_name in cross_pf_view.composites_deployment.items():
        if pf_name not in platforms:
            # PF not define
            warning("In cross_pf_view '%s', platform '%s' is not define in logical system"%(cross_pf_view.name, pf_name))

    # EUID binding with existing PF links
    for pf_link_id in cross_pf_view.euid_binding.keys():
        if pf_link_id not in platform_links:
            warning("In cross_pf_view '%s', platform link '%s' doesn't exist" % (cross_pf_view.name, pf_link_id))

    # wires are mapped on existing PF link
    for pf_link_id, wire in cross_pf_view.cross_PF_wire_mapping.items():
        if pf_link_id not in platform_links:
            warning("In cross_pf_view '%s', wire '%s' is mapped on an unknown platform link '%s'" %
                    (cross_pf_view.name, wire, pf_link_id))

    # [si upper composite]
    if not upper_composite.is_empty:
        for comp_name in upper_composite.components.keys():
            # composite not deployed
            if comp_name not in cross_pf_view.composites_deployment:
                warning("In cross_pf_view '%s', composite '%s' defined in '%s' is not deployed on a platform" %
                    (cross_pf_view.name, comp_name, upper_composite.name))

        for comp_name in cross_pf_view.composites_deployment.keys():
            # composite is not defined in upper composite
            if comp_name not in upper_composite.components:
                warning("In cross_pf_view '%s', composite '%s' is not defined in upper composite '%s'" %
                    (cross_pf_view.name, comp_name, upper_composite.name))

        # All wires is mapped on a PF link
        mapped_wires = sum(list(cross_pf_view.cross_PF_wire_mapping.values()), [])
        for wire in upper_composite.wires:
            if wire not in mapped_wires:
                error("In cross_pf_view '%s', wire '%s', is not mapped on a platform link" %
                         (cross_pf_view.name, wire))

        # All mapped wires exist
        for wire in mapped_wires:
            if wire not in list(upper_composite.wires):
                warning("In cross_pf_view '%s', mapped wire '%s' doesn't exist in upper composite '%s'" %
                         (cross_pf_view.name, wire, upper_composite.name))

