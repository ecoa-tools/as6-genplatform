# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

""" Generic ecoa item
"""

class ECOAitem:
    """ Class from which every model element is derived from
    """

    id_counter = 0

    def __init__(self, name):
        """ Initialisation with name and a static counter
        """
        self.name = name
        self.identifier = ECOAitem.id_counter
        ECOAitem.id_counter = ECOAitem.id_counter + 1

    def get_id(self):
        """ Get Id """
        return self.identifier

    def get_name(self):
        """ Get name """
        return self.name

