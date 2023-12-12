# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

import os
from xml.etree.ElementTree import ElementTree
from collections import OrderedDict

from ..utilities.logs import info, error
from ..utilities.xml_utils import validate_XML_file


def parse_nodes_deployment(integration_directory, xsd_directory):
    filename = os.path.join(integration_directory, "nodes_deployment.xml")
    if not os.path.exists(filename):
        info("File does not exist: " + filename)
        return None

    if validate_XML_file(filename, os.path.join(xsd_directory, "nodes-deployment.xsd")) == -1:
        return None

    tree = ElementTree()
    tree.parse(filename)

    l_nodes_address = OrderedDict()
    # protection domain
    for c_node in tree.iterfind("logicalComputingNode"):
        l_id = c_node.get("id")
        l_address = c_node.get("ipAddress")
        l_nodes_address[l_id] = l_address
    return l_nodes_address


def check_nodes_deployment(nodes_deployment, protection_domains):
    """Check logic of the nodes deployment file

     - detect if all protection domain have an associated ip address in nodes deployment file

    Args:
        nodes_deployment       (dict): The dictionary of nodes deployment
        protection_domains     (dict): The dictionary of protection domains

    @return     True or False
    """
    if nodes_deployment is None:
        info("No Nodes deployment")
        return True

    correct_file = True
    for pd in protection_domains.values():
        # detect if every protection domains have ip deployment properties
        if pd.node not in nodes_deployment:
            error("Protection domain '" + pd.name + "' doesn't have ip deployment properties")
            correct_file = False

    # detect if the platform main have ip deployment properties
    if "main" not in nodes_deployment:
        error("Platform 'main' doesn't have ip deployment properties")
        correct_file = False

    return correct_file
