# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

from collections import OrderedDict

class Logical_System:
    """Description of a logical system

    Attributes:
        name            (str): Name of logical system (xxx.logical_system.xml)
        platforms      (dict): Dictionary of :class:`.Platform`
        platform_links (dict): Dictionary of :class:`.PlatformLink`
    """
    def __init__(self, name):
        self.name = name
        self.platforms = OrderedDict()
        self.platform_links = OrderedDict()
