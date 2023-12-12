# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

class Link:
    id_counter = 0

    def __init__(self, sp, tp, throughput, latency):
        self.source_processor = sp
        self.target_processor = tp
        self.throughput = throughput
        self.latency = latency
        self.id = Link.id_counter
        Link.id_counter = Link.id_counter + 1

    def get_id(self):
        return self.id

    def get_name(self):
        return self.__repr__()

    def get_source_node(self):
        return self.source_processor

    def get_target_node(self):
        return self.target_processor

    def get_throughput(self):
        return self.throughput

    def get_latency(self):
        return self.latency

    def __repr__(self):
        return self.source_processor + ':' + \
               self.target_processor
