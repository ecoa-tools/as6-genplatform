# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

class LibrariesReferencesCycles:
    """The Libraries References Cycles class.
    
    Args:
        _libraries: The list of libraries.
        _graph: The directed graph encoding the references between libraries.
        _visited: The set of visited nodes.
        _path: The current path taken in the graph.
    """

    _libraries = None
    _graph = None
    _visited = None
    _path = None

    def __init__(self, libraries):
        self._libraries = libraries
        self._graph = self._init_graph()
        self._visited = set()
        self._path = []

    def _init_graph(self):
        """Converts the references between libraries into a directed graph.
        """
        graph = {}
        for library_name, (library, _) in self._libraries.items():
            graph[library_name] = library.included_libs
        return graph

    def _visit(self, node):
        """Visits a node of the graph to search references cycles from it.
        """
        if node in self._visited:
            return None
        self._visited.add(node)
        self._path.append(node)
        for neighbour in self._graph.get(node, []):
            if neighbour in self._path:
                return self._path[self._path.index(neighbour):] + [neighbour]
            cycle_found = self._visit(neighbour)
            if cycle_found:
                return cycle_found
        self._path.remove(node)
        return None

    def compute(self):
        """Computes all references cycles between libraries.
        
        Return:
            cycles (List[List[str]]): The references cycles.
        """
        cycles = []
        for node in self._graph:
            cycle = self._visit(node)
            if cycle:
                cycles.append(cycle)
        return cycles
