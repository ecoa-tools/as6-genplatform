# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

import os

class module_binary_desc:
    """Description of a binary module

    Attributes:
        mod_reference   (str): name of the :class:`.Module_Implementation`
        checksum        (str): NOT USED. checksum of the binary file
        heapSize        (str): NOT USED. module heap size
        stackSize       (str): NOT USED. module stack size
        userContextSize      (str): size of the user context in bytes
        warmStartContextSize (str): size of the warm context in bytes
        processorTarget_type (str): NOT USED. processor type name
        object_file          (str): binary file (absolute path)
    """
    def __init__(self, mod_reference,
                 checksum,
                 heapSize,
                 stackSize,
                 userContextSize,
                 warmStartContextSize,
                 processorTarget_type):

        self.mod_reference = mod_reference
        self.checksum = checksum
        self.heapSize = heapSize
        self.stackSize = stackSize
        self.userContextSize = userContextSize
        self.warmStartContextSize = warmStartContextSize
        self.processorTarget_type =processorTarget_type

    def set_object_file(self, object_file, bin_desc_file):
        """set the binary file. Create absolute path

        Attributes:
            object_file    (str): The object file (relative path from xml file)
            bin_desc_file  (str): The bin description file. Used to find absolute path of object file
        """
        self.object_file = os.path.join(os.path.dirname(bin_desc_file), object_file)

