# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

import os
from xml.etree.ElementTree import ElementTree
from ..utilities.namespaces import NameSpaces, ECOS_BIN
from ..utilities.xml_utils import validate_XML_file
from ..utilities.logs import debug, error, warning
from ..models.module_binary_desc import module_binary_desc

def parse_all_binary_desc(xsd_directory, component_implementations):
    """Parse binary descriptor file of every component implementations if exists.

    Arguments:
        xsd_directory (str): xsd directory to check xml files
        component_implementations (dict): dictionary of every :class:`~ecoa.models.component_implementation.Component_Implementation`
    """
    for comp_impl,_ in component_implementations.values():
        bin_desc_file = os.path.join(comp_impl.impl_directory, "bin-desc.xml")

        if os.path.isfile(bin_desc_file):
            parse_bin_desc(bin_desc_file,xsd_directory, comp_impl)
    check_binary_modules(component_implementations)

def parse_bin_desc(bin_desc_file,xsd_directory, comp_impl):
    """parse a bin-desc.xml file

    Arguments:
        bin_desc_file  (str): Binary descriptor file of a component implementation
        xsd_directory  (str): The xsd directory, used to check xml
        comp_impl      (:class:`~ecoa.models.component_implementation.Component_Implementation`):
            The component implementation of the binary descriptor file

    """
    if validate_XML_file(bin_desc_file, os.path.join(xsd_directory, "Schemas_ecoa","ecoa-bin-desc-2.0.xsd")) == -1:
        return

    # start parsing
    tree = ElementTree()
    tree.parse(bin_desc_file)
    comp_impl_name = tree.getroot().get("componentImplementation")
    if comp_impl_name != comp_impl.name:
        warning("binary descriptor file do not refer to the right component implementation (%s)"%bin_desc_file)

    processorTarget_type = tree.find(ECOS_BIN+"processorTarget").get("type")

    for binaryModule in tree.findall(ECOS_BIN+"binaryModule"):
        module_name = binaryModule.get('reference')
        object_name = binaryModule.get('object')
        checksum = binaryModule.get('checksum')
        heapSize = binaryModule.get('heapSize')
        stackSize = binaryModule.get('stackSize')
        userContextSize = binaryModule.get('userContextSize')
        warmStartContextSize = binaryModule.get('warmStartContextSize')

        if module_name not in comp_impl.module_implementations:
            error("module %s does not exist in component %s"%(module_name,comp_impl.name))
            return

        mod_impl = comp_impl.module_implementations[module_name]
        mod_impl.binary_desc = module_binary_desc(module_name,
                                                  checksum,
                                                  heapSize,
                                                  stackSize,
                                                  userContextSize,
                                                  warmStartContextSize,
                                                  processorTarget_type)
        mod_impl.binary_desc.set_object_file(object_name, bin_desc_file)

        if not os.path.isfile(mod_impl.binary_desc.object_file):
            warning("binary file not found : "+mod_impl.binary_desc.object_file)
        else:
            debug("binary file found for module %s in %s"%(mod_impl.name, comp_impl.name))

def check_binary_modules(component_implementations):
    """Check size of user_contect and warm_start_context.

    Size should be greater than zero if context is enable. Otherwize, warning message is emetted.
    """

    for comp_impl,_ in component_implementations.values():
        for mod_impl in comp_impl.module_implementations.values():
            mod_type = comp_impl.module_types[mod_impl.type]
            if  mod_impl.is_binary_module() \
                and mod_type.user_context \
                and mod_impl.binary_desc.userContextSize == "0" :
                warning("binary module %s in component implementation %s has a user context with a size equals to 0" % \
                        (mod_impl.name, comp_impl.name))
            if  mod_impl.is_binary_module() \
                and mod_type.warm_start_context \
                and mod_impl.binary_desc.warmStartContextSize == "0" :
                warning("binary module %s in component implementation %s has a warm start context with a size equals to 0" % \
                        (mod_impl.name, comp_impl.name))
