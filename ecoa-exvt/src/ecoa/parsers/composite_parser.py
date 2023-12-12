# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

from xml.etree.ElementTree import ElementTree
from ..models.component import Component
from ..models.wire import Wire
from ..utilities.namespaces import NameSpaces, CSA, ECOS_CSA, ECOS_SCA
from ..utilities.logs import debug, error, warning
from ..utilities.xml_utils import validate_XML_file
from ..models.property_classes import Composite_Property
import os
from ..models.composite import Composite


def parse_composite(xsd_directory, filename, libraries):

    ns = NameSpaces()
    ns.setup_parsing()

    if not os.path.exists(filename):
        error("Composite file '%s' does not exist" % (filename))
        return None


    if validate_XML_file(filename, xsd_directory + "/Schemas_ecoa/sca/sca-1.1-cd06-subset-2.0.xsd") == -1:
        return None

    # composite name
    composite_name = os.path.basename(filename)
    if composite_name.endswith(".impl.composite"):
        # final assembly
        composite_name = composite_name.replace(".impl.composite", "")
    elif composite_name.endswith(".composite"):
        # initial assembly
        composite_name = composite_name.replace(".composite", "")
    new_composite = Composite(composite_name)

    # parsing
    tree = ElementTree()
    tree.parse(filename)
    ## check name consitency
    real_composite_name = tree.getroot().get("name")
    if real_composite_name != composite_name:
        warning(("Composite '%s' must be defined in a file with prefix '%s'." +
                 "'%s' isn't a compliant filename")%
                (real_composite_name, real_composite_name, os.path.basename(filename)))
        new_composite.set_name(real_composite_name)

    ## composite references
    for ref_node in tree.iterfind(CSA + "reference"):
        ref_name = ref_node.get("name")
        ref_promote_str = ref_node.get("promote")
        new_composite.add_reference_promotion(ref_name, ref_promote_str)

    ## composite services
    for serv_node in tree.iterfind(CSA + "service"):
        serv_name = serv_node.get("name")
        serv_promote_str = serv_node.get("promote")
        new_composite.add_service_promotion(serv_name, serv_promote_str)


    ## Composite Properties
    for prop_node in tree.iterfind(CSA + "property"):
        prop_name = prop_node.get("name")
        prop_type = prop_node.get(ECOS_SCA + "type")
        prop_val = prop_node.find(CSA + "value").text
        if prop_name in new_composite.properties:
            warning("Composite property '"+prop_name+"' is already defined")
            continue
        new_composite.properties[prop_name] = Composite_Property(prop_name, prop_type, prop_val, libraries)
    debug("Composite properties:")
    for prop in new_composite.properties.values():
        debug("  "+ str(prop))

    # the tree root is the top level html element
    for c in tree.iterfind(CSA + "component"):
        cname = c.get("name")
        component = Component(cname)

        composite_root = c.find(CSA + "implementation.composite")
        composite_name = ""
        if composite_root != None:
            component.set_composite_name(composite_root.get("name"))

        for s in c.iterfind(ECOS_CSA + "instance"):
            name = s.get("componentType")
            component.set_component_type(name)
            for ci in s.iterfind(ECOS_CSA + "implementation"):
                name = ci.get("name")
                component.set_component_implementation(name)
        for s in c.iterfind(CSA + "service"):
            name = s.get("name")

            syntax_node = s.find(ECOS_SCA + "interface")
            syntax_name = ""
            if syntax_node != None :
                syntax_name = syntax_node.get("syntax")

            component.add_service(name, syntax_name)

        for ref in c.iterfind(CSA + "reference"):
            name = ref.get("name")

            syntax_node = ref.find(ECOS_SCA + "interface")
            syntax_name = ""
            if syntax_node != None :
                syntax_name = syntax_node.get("syntax")
            component.add_reference(name, syntax_name)

        # component properties
        for p_node in c.iterfind(CSA + "property"):
            p_name = p_node.get("name")
            p_val = None
            p_source = None
            p_val_node = p_node.find(CSA + "value")
            if p_val_node is not None:
                p_val = p_val_node.text
            else:
                p_source = p_node.get("source")
            component.add_property(p_name, p_val, p_source, new_composite.properties)

        if cname in new_composite.components:
            warning("The component instance %s is declared two times" % (cname))
        new_composite.components[cname] = component

    for n, c in new_composite.components.items():
        debug(c.to_string())
        debug("Name: %s %d (%s) %d %d" % (n, c.get_id(), c.get_component_type(), len(c.services), len(c.references)))

    for c in tree.iterfind(CSA + "wire"):
        (sc, ss) = c.get("source").split('/')
        (tc, ts) = c.get("target").split('/')

        w = Wire(sc, ss, tc, ts)
        new_composite.wires.add(w)

    for w in new_composite.wires:
        debug("Wire %s/%s => %s/%s" % \
             (w.get_source_component(), w.get_source_service(),
              w.get_target_component(), w.get_target_service()))



    new_composite.is_empty = False
    new_composite.wires = sorted(new_composite.wires)

    return new_composite



def get_required_wires(cn, sn, wires):
    wset = set()
    for w in wires:
        if w.get_source_component() == cn and w.get_source_service() == sn:
            wset.add(w)
    return wset


def get_provided_wires(cn, sn, wires):
    wset = set()
    for w in wires:
        if w.get_target_component() == cn and w.get_target_service() == sn:
            wset.add(w)
    return wset


def check_double_wires(wires):
    wset = []  # List
    for w in wires:
        for ww in wires:
            if (not w == ww) and (ww not in wset):
                if ww.get_source_component() == w.get_source_component() and \
                   ww.get_source_service() == w.get_source_service() and \
                   ww.get_target_component() == w.get_target_component() and \
                   ww.get_target_service() == w.get_target_service():
                    if w not in wset:
                        wset.append(w)
                    wset.append(ww)
                    error("Wire %s is declared double times" % w.__repr__())
                    continue
    return wset


def check_multiple_providers(wires):
    """check if wires do not have multiple providers

    Parameters:
        wires (list): list of :class:`.Wire`
    """
    for w in wires:
        for ww in wires:
            if not w == ww:
                if ww.get_source_component() == w.get_source_component() and \
                                ww.get_source_service() == w.get_source_service():
                    warning("ERROR ? : multiple providers for the same service ?? : "
                        + w.__repr__() + " and " + ww.__repr__())



def check_wires(components, wires):
    """Check wires logic:

     - check if components and services exist
     - check that two wires do not link both pairs of components/services
     - check that two wires do not link with the same provider (components/services)

    Parameters:
        components (list): The list of :class:`.Component`
        wires      (list): The list of :class:`.Wire`
    """
    ret_val = True
    for w in wires:
        scn = w.get_source_component()
        if scn in components:
            sc = components[scn]
            ss = w.get_source_service()
            if ss not in sc.references:
                error("Required service %s for wire %s does not exist" % \
                      (ss, w.__repr__()))
                ret_val = False
        else:
            error("Source component %s for wire %s does not exist" % \
                  (scn, w.__repr__()))
            ret_val = False

        tcn = w.get_target_component()
        if tcn in components:
            tc = components[tcn]
            ts = w.get_target_service()
            if ts not in tc.services:
                error("Provided service %s for wire %s does not exist" % \
                      (ts, w.__repr__()))
                ret_val = False
        else:
            error("Target component %s for wire %s does not exist" % \
                  (tcn, w.__repr__()))
            ret_val = False

    check_double_wires(wires)
    check_multiple_providers(wires)

    return ret_val

def check_composite_property(composite_properties, libraries):
    for pty in composite_properties.values():
        if pty.property_type.type is None:
            warning("Composite property '%s' type is not set" % pty.name)
            continue
        library_name, type_name = pty.property_type.type.split(":", 1)
        if not(library_name in libraries and libraries[library_name][0].is_datatype_defined(type_name)):
            warning("Composite property '%s' type is unknown : '%s'" % (pty.name, pty.property_type.type))

def check_component_consistency(component, component_type):
    # check service
    ## check service/reference in component_type are defined in component
    for serv in component_type.services:
        if serv.name not in component.services:
            warning("Component '%s' (from type '%s') doesn't defined service '%s'"\
                    %(component.name, component_type.name, serv.name))
    for ref in component_type.references:
        if ref.name not in component.references:
            warning("Component '%s' (from type '%s') doesn't defined reference '%s'"\
                    %(component.name, component_type.name, ref.name))

    ## check service/reference in component exist in component_type
    service_names = [v.name for v in component_type.services]
    for serv in component.services:
        if serv not in service_names:
            error("Component '%s' defines a service '%s' that doesn't exist in type '%s'"\
                    %(component.name, serv, component_type.name))
    reference_names = [v.name for v in component_type.references]
    for ref in component.references:
        if ref not in reference_names:
            error("Component '%s' defines a reference '%s' that doesn't exist in type '%s'"\
                    %(component.name, ref, component_type.name))

def check_component_propety(component, component_type, composite_properties):
    # check properties
    for prop_type in component_type.properties.values():
        ## check if property type has a value in component
        if prop_type.name not in component.properties:
            warning("Component '%s' is not consistent with '%s', property type'%s' has not value"\
                    %(component.name, component_type.name, prop_type.name))

    for prop in component.properties.values():
        ## check if property type exists in component type
        if prop.name not in component_type.properties:
            warning("Component '%s' is not consistent with '%s', property '%s' is not defined in component type"\
                    %(component.name, component_type.name, prop.name))
            continue

        if prop.source != None:
            ## Check if property reference exists
            if prop.source[1:] not in composite_properties:
                error("In component '%s', property '%s' refers to an unknown composite property '%s'"\
                        %(component.name, prop.name, prop.source))
                continue

            ## check type consitency between composite and component type
            prop_type = component_type.properties[prop.name]
            prop_composite = composite_properties[prop.source[1:]]
            if prop_type.type != prop_composite.property_type.type:
                warning("In component '%s', property '%s' type isn't consistent: '%s' != '%s'"\
                    %(component.name, prop.name,prop_type.type,prop_composite.property_type.type))


def check_final_composite(components, components_types, wires, composite_properties, libraries):
    ## check final assembly composite
    check_composite_property(composite_properties, libraries)

    for comp in components.values():
        # check if component type exist
        if comp.component_type not in components_types:
            warning("Type of component '%s' is unknown : '%s'" % (comp.name, comp.component_type))
        else:
            comp_type,_ = components_types[comp.component_type]
            check_component_consistency(comp, comp_type)
            check_component_propety(comp, comp_type,composite_properties)

    check_wires(components, wires)

def check_intial_composite(composite, components_types,  libraries):
    ## check composite defined in an intial assembly file
    check_promotion(composite)
    check_wires(composite.components, composite.wires)
    for comp in composite.components.values():
        # check if component type exist
        if comp.component_type not in components_types:
            warning("Type of component '%s' is unknown : '%s'" % (comp.name, comp.component_type))
        else:
            comp_type,_ = components_types[comp.component_type]
            check_component_consistency(comp, comp_type)

def check_upper_composite(upper_composite, service_definitions, platform_composites):
    """check upper composite at cross platform level
    """

    # check composite
    for comp in upper_composite.components.values():
        if comp.composite_name not in platform_composites:
            warning("In upper composite '%s', composite type '%s' of component '%s' is unknown" %
                    (upper_composite.name, comp.composite_name, comp.name))
        else:
            composite_type = platform_composites[comp.composite_name]

            for serv in comp.services:
                if serv not in composite_type.service_promotions:
                    warning("In upper composite '%s', in component '%s', service '%s' is not defined in composite type '%s'" %
                        (upper_composite.name, comp.name, serv, comp.composite_name))

            for ref in comp.references:
                if ref not in composite_type.reference_promotions:
                    warning("In upper composite '%s', in component '%s', reference '%s' is not defined in composite type '%s'" %
                        (upper_composite.name, comp.name, ref, comp.composite_name))

    # check wires consistency
    check_wires(upper_composite.components,upper_composite.wires)

    # check wire syntax
    for wire in upper_composite.wires:
        if wire.source_component not in upper_composite.components or \
            wire.target_component not in upper_composite.components:
            # error case
            continue

        source_comp = upper_composite.components[wire.source_component]
        target_comp = upper_composite.components[wire.target_component]

        # check
        if wire.source_service not in source_comp.references:
            warning("In upper composite '%s', for wire '%s', source service '%s' is not define in component '%s'" %
                    (upper_composite.name, wire, wire.source_service, wire.source_component))
            continue

        if wire.target_service not in target_comp.services:
            warning("In upper composite '%s', for wire '%s', target service '%s' is not define in component '%s'" %
                    (upper_composite.name, wire, wire.source_service, wire.target_component))
            continue

        # difference syntax
        source_syntax = source_comp.reference_syntaxes[wire.source_service]
        target_syntax = target_comp.service_syntaxes[wire.target_service]
        if source_syntax != target_syntax:
            warning("In upper composite '%s', for wire '%s', syntax are not consitence (%s != %s)" %
                    (upper_composite.name, wire, source_syntax, target_syntax))

        # not defined syntax
        if source_syntax not in service_definitions:
           warning("In upper composite '%s', for wire '%s', syntax is not defined '%s'" %
                        (upper_composite.name, wire, source_syntax))

        if target_syntax not in service_definitions:
           warning("In upper composite '%s', for wire '%s', syntax is not defined '%s'" %
                        (upper_composite.name, wire, target_syntax))

def check_promotion(composite):

    # check if promotion exists
    for ref_name, promoted_list in composite.reference_promotions.items():
        for comp_name, comp_ref_name in promoted_list:
            if comp_name not in composite.components:
                warning("In intial composite '%s', reference '%s' promote an unknwon component '%s'" %
                (composite.name, ref_name, comp_name) )
            else:
                if comp_ref_name not in composite.components[comp_name].references:
                    warning("In intial composite '%s', reference '%s' promotes a reference '%s' that doesn't exist in component '%s'" %
                            (composite.name, ref_name, comp_ref_name, comp_name))

    for serv_name, promoted_list in composite.service_promotions.items():
        for comp_name, comp_serv_name in promoted_list:
            if comp_name not in composite.components:
                warning("In intial composite '%s', service '%s' promote an unknwon component '%s'" %
                (composite.name, serv_name, comp_name) )
            else:
                if comp_serv_name not in composite.components[comp_name].services:
                    warning("In intial composite '%s', service '%s' promotes a service '%s' that doesn't exist in component '%s'" %
                            (composite.name, serv_name, comp_serv_name, comp_name))

    # check double promotion
    promoted_references = set()
    for ref_name, promoted_list in composite.reference_promotions.items():
        for comp_name, comp_ref_name in promoted_list:
            if comp_name+"/"+comp_ref_name not in promoted_references:
                promoted_references.add(comp_name+"/"+comp_ref_name)
            else:
                warning("In intial composite '%s', '%s/%s' is promoted many time" %
                            (composite.name,comp_name, comp_ref_name))

    promoted_services = set()
    for serv_name, promoted_list in composite.service_promotions.items():
        for comp_name, comp_serv_name in promoted_list:
            if comp_name+"/"+comp_serv_name not in promoted_services:
                promoted_services.add(comp_name+"/"+comp_serv_name)
            else:
                warning("In intial composite '%s', '%s/%s' is promoted many time" %
                            (composite.name,comp_name, comp_serv_name))


