# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

class Module_Implementation:
    """Describe a module implementation

    Attributes:
        name      (str): module implementation name
        mtype     (str): name of :class:`.Module_Type`
        mlanguage (str): module language implementation. 'C' by default
    """
    id_counter = 0  #:unique module implementation number

    def __init__(self, name, mtype="", mlanguage="C"):
        self.name = name
        self.id = Module_Implementation.id_counter
        self.type = mtype
        self.language = mlanguage
        self.binary_desc = None
        Module_Implementation.id_counter += 1

    def is_binary_module(self):
        return self.binary_desc != None

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_type(self):
        return self.type

    def get_language(self):
        return self.language
