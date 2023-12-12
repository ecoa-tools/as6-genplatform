# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

import os
from xml.etree.ElementTree import ElementTree
from ..utilities.logs import error
from ..utilities.xml_utils import validate_XML_file

class ECOAProject:
    def __init__(self, config_filename):
        self.filename = config_filename
        self.directory = os.path.dirname(self.filename)
        self.reset_project()
        self.output_dir = "."

    def reset_project(self):
        self.project_name = ""
        self.type_files = set()
        self.service_files = set()
        self.component_files = set()
        self.init_assembly_files = set()
        self.comp_impl_files = set()
        self.impl_assembly_files = set()
        self.deployment_files = set()
        self.logical_system_files = set()
        self.crossplatform_files = set()
        self.EUID_files = set()

    def get_cmd_line_output(self, output):
        if output:
            if os.path.isabs(output):
                self.output_dir = output
            else:
                self.output_dir = os.path.abspath(os.path.join(self.directory, output))
            return True
        return False

    def parse_output(self, output, xsd_directory):
        if xsd_directory:
            if os.path.exists(self.filename) is False:
                error("File does not exist for %s" % self.filename)
                return False

            if validate_XML_file(self.filename, xsd_directory + "/Schemas_ecoa/ecoa-project-2.0.xsd") == -1:
                return False

            ECOA_PROJECT = '{http://www.ecoa.technology/project-2.0}'

            tree = ElementTree()
            tree.parse(self.filename)

            # Use output from command line
            if not self.get_cmd_line_output(output):
                # Find output directory from project file
                find_dir=None
                for e in tree.findall(ECOA_PROJECT+"outputDirectory"):
                    if(e.text != None):
                        find_dir = e.text
                        break
                if find_dir:
                    self.output_dir = os.path.abspath(os.path.join(self.directory, find_dir))
                else:
                    # No output directory found
                    error("Missing output directory from command line or project file %s" % self.filename)
                    return False

            return True
        else:
            # Set output only from command line
            if not self.get_cmd_line_output(output):
                self.output_dir = os.path.abspath(self.directory)
            return True

    def parse_project(self, xsd_directory):
        if os.path.exists(self.filename) is False:
            error("File does not exist for %s" % self.filename)
            return False

        if validate_XML_file(self.filename, xsd_directory + "/Schemas_ecoa/ecoa-project-2.0.xsd") == -1:
            return False

        ECOA_PROJECT = '{http://www.ecoa.technology/project-2.0}'

        tree = ElementTree()
        tree.parse(self.filename)

        # Reset members in case of multiple calls
        self.reset_project()

        self.project_name =tree.getroot().get("name")

        #Find type files
        types_root = tree.find(ECOA_PROJECT+"types")
        if types_root != None:
            for type_file in types_root.iterfind(ECOA_PROJECT+"file"):
                self.type_files.add(os.path.join(self.directory, type_file.text))

        #Find service files
        service_root = tree.find(ECOA_PROJECT+"serviceDefinitions")
        if service_root != None:
            for serv_file in service_root.iterfind(ECOA_PROJECT+"file"):
                self.service_files.add(os.path.join(self.directory, serv_file.text))

        #Find component files
        component_root = tree.find(ECOA_PROJECT+"componentDefinitions")
        if component_root != None:
            for comp_file in component_root.iterfind(ECOA_PROJECT+"file"):
                self.component_files.add(os.path.join(self.directory, comp_file.text))

        #Find component implementation files
        comp_impl_root = tree.find(ECOA_PROJECT+"componentImplementations")
        if comp_impl_root != None:
            for comp_impl_file in comp_impl_root.iterfind(ECOA_PROJECT+"file"):
                self.comp_impl_files.add(os.path.join(self.directory, comp_impl_file.text))

        #Find initial assembly files
        self.init_assembly_files = set([os.path.join(self.directory, e.text) \
                                    for e in tree.findall(ECOA_PROJECT+"initialAssembly") if e.text != None])

        #Find implementation assembly files
        self.impl_assembly_files = set([os.path.join(self.directory, e.text) \
                                    for e in tree.findall(ECOA_PROJECT+"implementationAssembly") if e.text != None])

        #Find deployment files
        self.deployment_files = set([os.path.join(self.directory, e.text) \
                                    for e in tree.findall(ECOA_PROJECT+"deploymentSchema") if e.text != None])

        #find logical system files
        self.logical_system_files = set([os.path.join(self.directory, e.text) \
                                    for e in tree.findall(ECOA_PROJECT+"logicalSystem") if e.text != None])

        # find cross platform view files:
        self.crossplatform_files = set([os.path.join(self.directory, e.text )\
                                    for e in tree.findall(ECOA_PROJECT+"crossPlatformsView") if e.text != None])

        # Find EUIDS files
        for euids in tree.iterfind(ECOA_PROJECT+"EUIDs"):
            self.EUID_files.update(set([os.path.join(self.directory, e.text) \
                                        for e in euids.findall(ECOA_PROJECT+"EUID") if e.text != None]))

        return True
