# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

from xml.etree import ElementTree
from ecoa.utilities.namespaces import CSA, XS, ECOS_CSA


def harness_generate_component_type(new_services, new_references):
    ElementTree.register_namespace("", CSA[1:-1])
    ElementTree.register_namespace("xs",XS[1:-1])
    ElementTree.register_namespace("ecoa-sca",ECOS_CSA[1:-1])

    root = ElementTree.Element("componentType")
    root.attrib["xmlns"]=CSA[1:-1]
    root.attrib["xmlns:xs"]=XS[1:-1]

    for service_name, (syntax,_) in new_services.items():
        new_elt = ElementTree.Element("service")
        new_elt.set("name", service_name)
        ElementTree.SubElement(new_elt, ECOS_CSA+"interface", attrib={"syntax":syntax.name})
        root.append(new_elt)

    for reference_name, (syntax,_) in new_references.items():
        new_elt = ElementTree.Element("reference")
        new_elt.set("name", reference_name)
        ElementTree.SubElement(new_elt, ECOS_CSA+"interface", attrib={"syntax":syntax.name})
        root.append(new_elt)

    return root
