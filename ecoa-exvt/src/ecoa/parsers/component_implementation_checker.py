# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

from ..utilities.logs import error, warning

def __comp_impl_check_param_type(libraries, comp_impl, dtype):
    lib_name, type_name = dtype.split(':')
    if (lib_name not in comp_impl.libraries) \
            or (not libraries[lib_name][0].is_datatype_defined(type_name)):
        error("I component implementation %s,  unknow type %s" % (comp_impl.name, dtype))
        return False
    return True

def __check_link_type_module(link, operation_type):
    """Check if link nature complies with operation type. for exemple, datalink uses with a RequestReceived module operation -> not conforming
    """
    ret_value = True
    if link.type == 'event':
        if operation_type.type not in ['ES', 'ER']:
            ret_value = False
    elif link.type == 'RR':
        if operation_type.type not in ['SRS', 'ARS', 'RR']:
            ret_value = False
    else:
        if operation_type.type not in ['DW', 'DR', 'DRN']:
            ret_value = False

    if not ret_value:
        error("[link " +link.get_op_id() +"] link do not comply with operation "+ operation_type.name+ "( op type: "
            + operation_type.type+", link type: "+ link.type+")")

    return ret_value

def __check_link_type_serv(link, operation_dnf, is_target, check_a_service):
     ## check operation type
    ret_value = True
    if link.type == 'RR' and operation_dnf.nature != 'RR':
        ret_value = False
    elif link.type == 'data' and operation_dnf.nature != 'DATA':
        ret_value = False
    elif link.type == 'event':
        if operation_dnf.nature == 'CMD':
            if check_a_service and is_target:
                ret_value = False
            elif not check_a_service and not is_target:
                ret_value = False
        elif operation_dnf.nature == 'NOTIFY':
            if check_a_service and not is_target:
                ret_value = False
            elif not check_a_service and is_target:
                ret_value = False
        else:
            ret_value = False

    if not ret_value:
        error("[link " +link.get_op_id() +"] link do not comply with service operation "+ operation_dnf.name+ " ( service operation nature: "
            + operation_dnf.nature+", link type: "+ link.type+"). Tips: check operation type and SENT/RECEIVED_BY_PROVIDER direction.")


    return ret_value

def __check_connected_operations(component_impl, mod_type, operation):
    if operation.type in ['ES','ARS','SRS','DW','DR','DRN']:
        for m_inst in component_impl.module_instances:
            m_inst_mod_type = component_impl.find_module_type(m_inst.name)
            if m_inst_mod_type.name == mod_type.name:
                found=False

                for link in component_impl.links:
                    if operation.type in ['DR','DRN']: # specific case for DataRead DataReadNotify
                        if operation.name == link.target_operation:
                            if link.target == m_inst.name:
                                found=True
                    else:
                        if operation.name == link.source_operation:
                            if link.source == m_inst.name:
                                found=True

                if not found:
                    warning("Operation [" +operation.name +"] of type " +operation.type + " defined in moduleType [" +mod_type.name
                            +"] not connected for instance [" +m_inst.name +"] in componentImplementation [" +component_impl.name+"]")

def __check_module_pinfo(mod_inst, mod_type, component):
    success = True
        # Pinfo should be defined in module instace
    for pinfo_type in mod_type.private_pinfo+mod_type.public_pinfo:
        if pinfo_type not in mod_inst.pinfo:
            error("In component implementation '%s', module instance '%s' doesn't defined Pinfo '%s'"\
                %(component.component_implementation, mod_inst.name, pinfo_type))
            success = False

    # If pinfo is defined by a reference, it should be defined by the component
    for pinfo in mod_inst.pinfo.values():
        if pinfo.pinfo_value[0] == '$':
            if pinfo.pinfo_value[1:] not in component.properties:
                error("In component implementation '%s' and module instance '%s', Pinfo '%s' refers to unkown reference '%s'"\
                    %(component.component_implementation, mod_inst.name, pinfo.name,pinfo.pinfo_value))
                success = False
    return success

def __check_module_properties(mod_inst, mod_type, component):
    success = True

    # properties should be defined in module instace
    for prop_type in mod_type.properties:
        if prop_type not in mod_inst.property_values:
            warning("In component implementation '%s', module instance '%s' doesn't defined property '%s'"\
                %(component.component_implementation, mod_inst.name, prop_type))

    # property references should be defined in component
    for prop in mod_inst.property_values.values():
        if prop.value[0] == '$':
            if prop.value[1:] not in component.properties:
                error("In component implementation '%s' and module instance '%s', property '%s' refers to unkown reference '%s'"\
                    %(component.component_implementation, mod_inst.name, prop.name,prop.value))
                success = False

    return success

def __check_mod_link_edge(mod_name, op_name, link, comp_impl):
    # check target or source of a link
    # - check link type / operation
    # - find parameters type

    parameter_types = []
    success = True
    if comp_impl.is_module_instance(mod_name):
        mod_type = comp_impl.find_module_type(mod_name)
        if op_name in mod_type.operations:
            if not __check_link_type_module(link, mod_type.operations[op_name]):
                success = False
            parameter_types =  [p.type for p in mod_type.operations[op_name].params]
        else:
            error("In component impl '%s', Invalid link : operation '%s' doesn't exist in module instance '%s'"\
                    %(comp_impl.name, op_name, mod_name))
            success = False

    elif comp_impl.is_dynamic_trigger_instance(mod_name):
        #dynamic trigger : reset, in, out
        if op_name == 'in':
            parameter_types = [p.type for p in comp_impl.get_instance(mod_name).params]
        elif op_name == 'out':
            parameter_types = [p.type for p in comp_impl.get_instance(mod_name).params]
            parameter_types = parameter_types[1:] # remove first parameters (ECOA:duration)
        elif op_name == "reset":
            pass
        else:
            error("In component impl '%s', Invalid link : operation '%s' doesn't exist in dynamic trigger '%s'"\
                    %(comp_impl.name, op_name, mod_name))
            success = False
    else:
        # trigger
        pass

    return success, parameter_types

def __check_serv_link_edge(serv_name, op_name, link, comp, serv_definition, is_target):
    # check target or source of a link
    # - check link type / operation
    # - find parameters type

    success = True
    parameter_types = []
    if serv_name in comp.services + comp.references:
        operation = serv_definition.find_operation(op_name)
        if operation != None:
            if not __check_link_type_serv(link, operation, is_target, (serv_name in comp.services)):
                success = False
            if operation.nature == 'DATA':
                parameter_types = [operation.params[0].type]
            else:
                parameter_types = [p.type for p in operation.params]
        else:
            error("In component imp '%s', Invalid link: operation '%s' doesn't exist in service/reference '%s'"\
                    %(comp.component_implementation, op_name, serv_name))
            success = False
    else:
        # could never happend
        success = False
    return success, parameter_types

## Check if component implementation is consistent to the previously defined module, trigger,
# service_definitions and operations defined
def check_component_implementation(component, component_impl, component_type,
                                    service_definitions, libraries):
    """ Check the consistency of a component implementation definition
    """

    success = True


    # Check libraries
    for lib_name in component_impl.libraries:
        if lib_name not in libraries:
            error("In component implementation %s, Unknown library %s" % (component_impl.name, lib_name))
            success = False

    # Check module type
    for mod_type in component_impl.module_types.values():
        for op in mod_type.operations.values():
            __check_connected_operations(component_impl, mod_type, op) ## to move

            ## Check parameters of module type operations
            for param in op.params:
                if not __comp_impl_check_param_type(libraries, component_impl, param.type):
                    success = False

        ## Check types of  module type properties
        for prop in mod_type.properties.values():
            if not __comp_impl_check_param_type(libraries, component_impl, prop.type):
                success = False

    # Check Module Instance
    for mod_inst in component_impl.module_instances:
        mod_type = component_impl.find_module_type(mod_inst.name)

        ## Check Pinfos
        if not __check_module_pinfo(mod_inst, mod_type, component):
            success = False

        ## Check properties
        if not __check_module_properties(mod_inst, mod_type, component):
            success = False

    # Check Dynamic Trigger Instance
    for dyn_trig in component_impl.dynamic_trigger_instances :
        # check parameter types
        for param in dyn_trig.params:
            if not __comp_impl_check_param_type(libraries, component_impl, param.type):
                success = False

    # Check versioned data
    for vd in component_impl.component_VDs:
        if not vd.accessControl:
            # check readers and writers are modules:
            for mod_name in list(vd.readers_dict.keys()) + list(vd.writters_dict.keys()):
                if not component_impl.is_module_instance(mod_name):
                    error("In component implementation '%s': '%s' is not a module but is used with a VD without access control" \
                        % (component_impl.name, mod_name))
    # Check links:
    #  - source and target
    #  - operation names
    #  - parameters consitent between source and target
    for link in component_impl.links:
        source_param_types = None
        target_param_types = None
        if component_impl.is_generic_module_instance(link.source):
            success, source_param_types = __check_mod_link_edge(link.source, link.source_operation, link, component_impl)
        elif link.source in component.services + component.references:
            sdefinition,_ = service_definitions[component_type.find_service_syntax(link.source)]
            success, source_param_types = __check_serv_link_edge(link.source, link.source_operation, link, component, sdefinition, False)
        elif link.is_external()\
            or (link.type=='data' and link.target == ""): #data without reader
            continue
        else:
            # error
            error("In component impl '%s', invalid link: source '%s' doesn't exist"\
                    %(component_impl.name, link.source))
            success = False
            continue

        if component_impl.is_generic_module_instance(link.target):
            success, target_param_types = __check_mod_link_edge(link.target, link.target_operation, link, component_impl)
        elif link.target in component.services + component.references:
            sdefinition,_ = service_definitions[component_type.find_service_syntax(link.target)]
            success, target_param_types = __check_serv_link_edge(link.target, link.target_operation, link, component, sdefinition, True)
        elif link.is_external()\
            or (link.type=='data' and link.target == ""): #data without reader
            continue
        else:
            # error
            error("In component impl '%s', invalid link: target '%s' doesn't exist"\
                    %(component_impl.name, link.target))
            success = False
            continue

        ## check source/target parameters
        if len(source_param_types) == len(target_param_types):
            for i,p_type in enumerate(source_param_types):
                if p_type != target_param_types[i]:
                    warning("In component '%s', invalid link: operation types may be not " %(component.name)\
                            +"consistent between source '%s' (%s) and target '%s' (%s) : %s, %s"\
                            %(link.source, link.source_operation, link.target, link.target_operation,\
                              source_param_types, target_param_types))
        else:
            error("In component '%s', invalid link: operation types are not " %(component.name)\
                    +"consistent between source '%s' (%s) and target '%s' (%s) : %s, %s"\
                    %(link.source, link.source_operation, link.target, link.target_operation,\
                      source_param_types, target_param_types))
            success = False

    return success
