# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

import os
from xml.etree.ElementTree import ElementTree
from ..models.platform import Platform
from ..models.platform_link import PlatformLink, udp_binding
from ..models.node import Node
from ..models.node_link import Link
from ..models.logical_system import Logical_System
from ..utilities.logs import debug, error, warning
from ..utilities.xml_utils import validate_XML_file

def parse_all_logicalsystem(xsd_directory, filename_list,):
    new_logical_system = None
    for file in filename_list:
        #TODO useless loop because only a unique logical system is supported

        if os.path.exists(file) is False:
            error("File '%s' does not exist" % file)
            return False

        if validate_XML_file(file, xsd_directory + "/Schemas_ecoa/ecoa-logicalsystem-2.0.xsd") == -1:
            return False

        logical_system_name = os.path.basename(file)
        if logical_system_name.endswith(".logical-system.xml"):
            # normal case. filename = #name#.logical-system.xml
            logical_system_name= logical_system_name.replace(".logical-system.xml", "")
        else:
            # support non-compliant filename
            warning("Logical system '%s' isn't a compliant filename, it should be '#name#.logical-system.xml'"%
                    (os.path.basename(file)))
            logical_system_name = logical_system_name.replace(".xml", "")

        new_logical_system = Logical_System(logical_system_name)
        parse_logicalsystem(file, new_logical_system, xsd_directory)

    return new_logical_system # currently only one logical system is supported

def parse_logicalsystem(filename, logical_system, xsd_directory):
    tree = ElementTree()
    tree.parse(filename)

    # Platforms
    for p in tree.iterfind("logicalComputingPlatform"):
        pid = p.get("id")
        ELI_ID = p.get("ELIPlatformId", default="")
        if pid in logical_system.platforms:
            debug("The platform %s has already been declared" % (pid))
            continue

        platform = Platform(pid, ELI_ID)

        for n in p.iterfind("logicalComputingNode"):
            nid = n.get("id")
            node = Node(nid)
            for lp in n.iterfind("logicalProcessors"):
                number = lp.get("number")
                p_type = lp.get("type")
                d = lp.find("stepDuration").get("nanoSeconds")
                node.add_logical_processors(int(number), p_type, int(d))

            number = n.find("moduleSwitchTime").get("microSeconds")
            node.set_module_switch_time(int(number))

            if (nid in platform.nodes) is True:
                warning("The node %s is declared two times in platform %s" % (nid, pid))
            platform.add_logical_node(node)

        for links_set in p.iterfind("logicalComputingNodeLinks"):
            for ln in links_set.iterfind("link"):
                from_p = ln.get("from")
                to_p = ln.get("to")
                throughput_node = ln.find("throughput")
                latency_node = ln.find("latency")
                tv = throughput_node.get("megaBytesPerSecond") if throughput_node != None else "-1"
                lv = latency_node.get("microSeconds") if latency_node != None else "-1"
                link = Link(from_p, to_p, int(tv), int(lv))
                platform.add_node_link(link)
        logical_system.platforms[pid] = platform

        for nid, n in platform.nodes.items():
            debug("Name: %s %d %d %d %d" % \
                  (nid, n.get_id(), n.get_processors_number(),
                   n.get_mean_step_duration(),
                   n.get_module_switch_time()))

        for link in platform.node_links:
            debug("Link %s => %s:%s - %d:%d" % \
                  (link.get_id(), link.get_source_node(), link.get_target_node(),
                   link.get_throughput(), link.get_latency()))

        check_node_links(platform.nodes, platform.node_links)


    for pid, p in logical_system.platforms.items():
        debug("Platform: %s %d %d %d %d" % \
              (pid, p.get_id(), p.get_processors_number(),
               p.get_mean_step_duration(),
               p.get_mean_module_switch_time()))

    # Platform links
    for links_set in tree.iterfind("logicalComputingPlatformLinks"):
        for ln in links_set.iterfind("link"):
            from_p = ln.get("from")
            to_p = ln.get("to")
            id_link = ln.get("id")
            throughput_node = ln.find("throughput")
            latency_node = ln.find("latency")

            tv = throughput_node.get("megaBytesPerSecond") if throughput_node != None else "-1"
            lv = latency_node.get("microSeconds") if latency_node != None else "-1"

            if id_link in logical_system.platform_links:
                warning("platform links id '%s' already exist" %(id_link))
                continue

            link = PlatformLink(id_link, from_p, to_p, int(tv), int(lv))

            transportBinding_node = ln.find("transportBinding")
            if transportBinding_node != None:
                protocol = transportBinding_node.get("protocol")
                param = transportBinding_node.get("parameters")
                link.protocol = protocol
                if protocol == "UDP":
                    ## parse specific transport binding file
                    binding_file = os.path.join(os.path.dirname(filename), param)
                    link.link_binding = parse_udp_binding_file(binding_file, xsd_directory)
                else:
                    warning("platform link '%s' uses an unknown protocol '%s'" % (id_link, protocol))
            else:
                warning("platform link '%s' has no transport binding" % (id_link))

            logical_system.platform_links[id_link]=link

    for link in logical_system.platform_links.values():
        debug("Link %s => %s:%s - %d:%d" % \
              (link.get_id(), link.get_source_platform(), link.get_target_platform(),
               link.get_throughput(), link.get_latency()))

    check_platform_links(logical_system)
    for pf in tree.iterfind("logicalComputingPlatform"):
            pid = pf.get("id")
    return tree

def parse_udp_binding_file(binding_file, xsd_directory):
    if os.path.exists(binding_file) is False:
        error("File '%s' does not exist" % binding_file)
        return None

    if validate_XML_file(binding_file, xsd_directory + "/Schemas_ecoa/guidance/ecoa-udpbinding-2.0.xsd") == -1:
        return None

    tree = ElementTree()
    tree.parse(binding_file)
    binding = udp_binding(binding_file)

    UDP_BINDING_SPACE = '{http://www.ecoa.technology/udpbinding-2.0}'

    for pf_node in tree.iterfind(UDP_BINDING_SPACE+"platform"):
        pf_name = pf_node.get("name")
        pf_id = pf_node.get("platformId")
        mcast_addr = pf_node.get("receivingMulticastAddress")
        port = pf_node.get("receivingPort")
        max_channel = int(pf_node.get("maxChannels", default="15"))
        binding.add_platform(pf_name, mcast_addr, port, pf_id, max_channel)

    return binding

def check_double_platform_links(links):
    lset = []  # List
    for l in links:
        for ll in links:
            if (l != ll) and (ll not in lset):
                if ll.get_source_platform() == l.get_source_platform()\
                        and ll.get_target_platform() == l.get_target_platform():
                    if l not in lset:
                        lset.append(l)
                    lset.append(ll)
                    warning("Link %s is declared double times" % l.__repr__())
    return lset

def check_platform_links(logical_system):
    """Check_platform_links :

        - check if platforms exists
        - check that two links do not link both pairs of platforms
        - check binding :
            * source and target PF must be defined in binding file
            * PF link should be find in binding file
    """
    for l in logical_system.platform_links.values():
        sp = l.get_source_platform()
        if sp not in logical_system.platforms:
            error("Source node %s for link %s does not exist" % \
                  (sp, l.__repr__()))
        tp = l.get_target_platform()
        if tp not in logical_system.platforms:
            error("Target node %s for link %s does not exist" % \
                  (tp, l.__repr__()))
        if l.link_binding != None:
            if sp not in l.link_binding.platforms:
                error("In PF link '%s', source platform '%s' is not defined in binding" %(l.name, sp))

            if tp not in l.link_binding.platforms:
                error("In PF link '%s', target platform '%s' is not defined in binding" %(l.name, sp))
        else:
            error("PF link '%s' has no binding" %(l.name))




#TODO: to remove ? :
def check_double_node_links(links):
    lset = []  # List
    for l in links:
        for ll in links:
            if (l != ll) and (ll not in lset):
                if ll.get_source_node() == l.get_source_node() and \
                                ll.get_target_node() == l.get_target_node():
                    if l not in lset:
                        lset.append(l)
                    lset.append(ll)
                    warning("Link %s is declared double times" % l.__repr__())
    return lset

def check_node_links(nodes, node_links):
    """ Check_node_links:

        * check if nodes exist
        * check that two links do not link both pairs of nodes
    """
    for l in node_links:
        sp = l.get_source_node()
        if sp not in nodes:
            error("Source node %s for link %s does not exist" % \
                  (sp, l.__repr__()))
        tp = l.get_target_node()
        if tp not in nodes:
            error("Target node %s for link %s does not exist" % \
                  (tp, l.__repr__()))
    check_double_node_links(node_links)
