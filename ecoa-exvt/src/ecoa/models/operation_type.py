# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

class Parameter:
    """ Parameter of a module operation

    Attributes:
        name        (str)  : parameter name
        type        (str)  : parameter type
        is_complex  (bool) : True if parameter type is a complex type (ie: a pointer will be used)
        direction   (str)  : 'input' or 'output'
    """

    def __init__(self, name, type, direction, is_complex=False):
        if type.find(":") == -1:
            type = 'ECOA:'+type
        self.name = name
        self.type = type
        self.is_complex = is_complex
        self.direction = direction

    def fill_type_property(self, libraries):
        """Fill 'is_complex' attribute

        :param dict libraries: key : library name; values : tuple
            (:class:`.Library`,  elementTree)
        """

        for l, _ in libraries.values():
            start = self.type.find(':')
            if l.is_datatype_defined(self.type[start + 1:]):
                self.is_complex = l.get_data_type(self.type[start + 1:]).is_complex_type()
                pass

    def get_libname(self):
        start = self.type.find(':')
        if start == -1:
            return 'ECOA'
        else:
            return self.type.split(":")[0]

    def get_typename(self):
        start = self.type.find(':')
        if start == -1:
            return self.type
        else:
            return self.type.split(":")[1]



##################
class Module_Operation_Type:
    """Class for a module operation type

    Attributes:
        id_counter  (int) : unique number
        name        (str) : operation name
        type        (str) : operation type : ES, ER, SRS, ARS, RR, DW, DR, DRN
        mot_params  (list): list of :class:`.Parameter`
        op_output_index (int): output operation index(some operation like RR can be intput and output)
        op_input_index  (int): inptu operation index (some operation like RR can be intput and output)
    """
    id_counter = 0

    def __init__(self, name, mot, mot_params):
        self.name = name
        self.id = Module_Operation_Type.id_counter
        self.type = mot
        self.params = mot_params
        self.op_output_index = -1
        self.op_input_index = -1

        Module_Operation_Type.id_counter = Module_Operation_Type.id_counter + 1

    def get_id(self):
        return self.id

    def get_type(self):
        return self.type

    def get_name(self):
        return self.name

    def get_params(self):
        return self.params


class Module_Event_Operation(Module_Operation_Type):
    """Class based on :class:`.Module_Operation_Type` for simple Event

    Note:
        Operation `type` is ES or ER
    """

    def __init__(self, name, mot, mot_params):
        super().__init__(name, mot, mot_params)

    def __str__(self):
        return self.name +"(type: "+ self.type +" output index: "+str(self.op_output_index)+")"


class Module_RR_Operation(Module_Operation_Type):
    """Class based on :class:`.Module_Operation_Type` for Request-Response operations

    Attributes:
        timeout     (float): timeout of the request used for ARS or SRS type
        maxVersions  (int)  : maximum number of concurrent Requests
        RR_op_index  (int) :  local index in module type. It is used by C code to
                              update the current number of concurrent RR for an operation

    Note:
        Operation `type` is SRS, ARS or RR
    """

    def __init__(self, name, mot, mot_params, timeout, maxConcurentRequest):
        super().__init__(name, mot, mot_params)
        #: timeout to unblock synchronous RR or inform about a failed asynchronous RR
        # (only used for RR operation)
        self.timeout = timeout
        self.maxVersions = maxConcurentRequest  #: max concurrent Requests
        self.RR_op_index = -1

    def __str__(self):
        return self.name +"(type: "+ self.type +" output index: "+str(self.op_output_index)\
               +" max: " + str(self.maxVersions)+")"


class Module_VD_Operation(Module_Operation_Type):
    """Class based on :class:`.Module_Operation_Type` for Versioned Data operations

    Attributes:
        maxVersions      (int): maximum number of versioned data copy used by the module
        module_VD_op_index  (int): used to retrieve local (in module) information in C code
        write_only         (bool): True if Written Data operation is in WriteOnly mode, otherwise False

    Note:
        Operation `type` is DW, DR or DRN
    """

    def __init__(self, name, mot, mot_params, maxVersions, write_only=False):
        super().__init__(name, mot, mot_params)
        self.maxVersions = maxVersions
        self.module_VD_op_index = -1
        if(write_only):
            self.mode = "WRITE_ONLY"
        else:
            self.mode = "READ_WRITE"


    def __str__(self):
        return self.name +"(type: "+ self.type +" output index: "+str(self.op_output_index)\
               +" max: " +str(self.maxVersions)+")"
