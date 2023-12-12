# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

class Platform_Configuration:
    """Platform instance described in deployement.xml

    Attributes:
        name              (str) : name of the platform
        fifo_size         (int) : size of FIFOs
        computing_nodes   (list): list of computing node IDs
    """

    def __init__(self, name, notificationMaxNumber):
        self.name = name
        self.fifo_size = notificationMaxNumber
        self.computing_nodes = []
        self.platform_message_link = ""

    def add_computing_node(self, node_ID):
        #: TODO add schedulingInformation
        self.computing_nodes.append(node_ID)
