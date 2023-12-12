# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

""" namespaces module """
import xml

CSA = '{http://docs.oasis-open.org/ns/opencsa/sca/200912}'
ECOS_CSA = '{http://www.ecoa.technology/sca-extension-2.0}'
ECOS_SCA = '{http://www.ecoa.technology/sca-extension-2.0}'
ECOS_IF = '{http://www.ecoa.technology/interface-2.0}'
ECOS_IFQ = '{http://www.ecoa.technology/interface-qos-2.0}'
ECOS_TYPES = '{http://www.ecoa.technology/types-2.0}'
ECOS_LS = '{http://www.ecoa.technology/logicalsystem-2.0}'
ECOS_CI = '{http://www.ecoa.technology/implementation-2.0}'
ECOS_MB = '{http://www.ecoa.technology/module-behaviour-2.0}'
ECOS_DE = '{http://www.ecoa.technology/deployment-2.0}'
ECOS_BIN = '{http://www.ecoa.technology/bin-desc-2.0}'
ECOS_UID = '{http://www.ecoa.technology/uid-2.0}'
ECOS_VIEW = '{http://www.ecoa.technology/cross-platforms-view-2.0}'
GRAPHML = '{http://graphml.graphdrawing.org/xmlns}'
YED = '{http://www.yworks.com/xml/graphml}'
PARSEC_CONFIG = '{http://www.dassault-aviation.com/parsec-config-1.0}'
XS = '{http://www.w3.org/2001/XMLSchema}'
ECOA_PROJECT = '{http://www.ecoa.technology/project-2.0}'

class NameSpaces(object):
    """ Class to initialize etree namespaces

            ns = NameSpaces()
            ns.setup_parsing()

    """

    def __init__(self):
        self.initialization_flag = False

    def setup_parsing(self):
        """ Register XSD namespaces within the etree package """
        if self.initialization_flag is False:
            xml.etree.ElementTree.register_namespace("csa", CSA[1:-1])
            xml.etree.ElementTree.register_namespace("ecos-csa", ECOS_CSA[1:-1])
            xml.etree.ElementTree.register_namespace("ecos-sca", ECOS_SCA[1:-1])
            xml.etree.ElementTree.register_namespace("ecos-if", ECOS_IF[1:-1])
            xml.etree.ElementTree.register_namespace("ecos-ifq", ECOS_IFQ[1:-1])
            xml.etree.ElementTree.register_namespace("ecos-types", ECOS_TYPES[1:-1])
            xml.etree.ElementTree.register_namespace("ecos-ls", ECOS_LS[1:-1])
            xml.etree.ElementTree.register_namespace("ecos-ci", ECOS_CI[1:-1])
            xml.etree.ElementTree.register_namespace("ecos-mb", ECOS_MB[1:-1])
            xml.etree.ElementTree.register_namespace("ecos-de", ECOS_DE[1:-1])
            xml.etree.ElementTree.register_namespace("", GRAPHML[1:-1])
            xml.etree.ElementTree.register_namespace("y", YED[1:-1])
            xml.etree.ElementTree.register_namespace("parsec-config", PARSEC_CONFIG[1:-1])
            self.initialization_flag = True


__all__ = [
    "CSA",
    "ECOS_CSA",
    "ECOS_SCA",
    "ECOS_IF",
    "ECOS_IFQ",
    "ECOS_TYPES",
    "ECOS_LS",
    "ECOS_CI",
    "ECOS_MB",
    "ECOS_DE",
    "GRAPHML",
    "YED",
    "PARSEC_CONFIG",
    ]


