# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

from lxml import etree
import os
import shutil
from ecoa.utilities.logs import error, info
from ecoa_asctg.generators.Harness_Component.harness_generator import harness_generate
from ecoa_asctg.generators.Harness_Component.harness_utils import get_harness_type_str, get_harness_str, \
    suffixed_harness_filename
from ecoa.ecoa_global_config import ECOA_Global_Config


class ECOA_Harness_Config(ECOA_Global_Config):
    """
    @brief      main class that extend all configuration information to generate platform harness
    """

    def __init__(self, working_directory, platform_config_file, verbosity=3):
        super().__init__(working_directory, platform_config_file, verbosity=verbosity)
        self.harness_components = []
        self.m_harness_comp_type_file = ""
        self.m_harness_comp_impl_file = ""
        self.m_composite_filename = ""
        self.m_deployment_filename = ""

    def get_harness_comp_type_file(self):
        harness_type_comp_name = get_harness_type_str()
        if len(list(self.ECOAProject.component_files)) == 0:
            # if no component in project
            comp_type_dir = harness_type_comp_name
        else:
            comp_type_dir = os.path.join(os.path.dirname(list(self.ECOAProject.component_files)[0]),
                                         "..", harness_type_comp_name)
        return os.path.normpath(os.path.join(comp_type_dir, harness_type_comp_name + ".componentType"))

    def get_harness_comp_impl_file(self):
        harness_comp_name = get_harness_str()
        if len(list(self.ECOAProject.comp_impl_files)) == 0:
            harness_comp_impl_dir = harness_comp_name
        else:
            harness_comp_impl_dir = os.path.join(os.path.dirname(list(self.ECOAProject.comp_impl_files)[0]),
                                                 "..", harness_comp_name)
        return os.path.normpath(os.path.join(harness_comp_impl_dir, harness_comp_name +".impl.xml"))

    def parse_project(self, xsd_directory):
        self.ECOAProject.parse_project(xsd_directory)
        self.m_harness_comp_type_file = self.get_harness_comp_type_file()
        self.m_harness_comp_impl_file = self.get_harness_comp_impl_file()
        self.m_composite_filename = list(self.ECOAProject.impl_assembly_files)[0]
        self.m_deployment_filename = list(self.ECOAProject.deployment_files)[0]
        self.m_harness_project_filename = suffixed_harness_filename(self.platform_config_file)
        self.m_harness_composite_filename = suffixed_harness_filename(self.m_composite_filename)
        self.m_harness_deployment_filename = suffixed_harness_filename(self.m_deployment_filename)

    def copy_and_check_project(self, xsd_directory, force_flag):
        self.parse_project(xsd_directory)

        if os.path.abspath(self.ECOAProject.directory) != self.ECOAProject.output_dir:
            if os.path.exists(self.ECOAProject.output_dir):
                if force_flag:
                    shutil.rmtree(self.ECOAProject.output_dir)
                    info("Harness component removed in '%s'" % self.ECOAProject.output_dir)
                else:
                    error("Harness component already generated in '%s' can't override" % self.ECOAProject.output_dir)
                    return False
            shutil.copytree(
                src=self.ECOAProject.directory,
                dst=self.ECOAProject.output_dir)
        else:
            # Check previous Harness generation
            if os.path.exists(self.m_harness_comp_type_file):
                if force_flag:
                    shutil.rmtree(os.path.dirname(self.m_harness_comp_type_file))
                    shutil.rmtree(os.path.dirname(self.m_harness_comp_impl_file))
                    if os.path.exists(self.m_harness_composite_filename):
                        os.remove(self.m_harness_composite_filename)
                    if os.path.exists(self.m_harness_deployment_filename):
                        os.remove(self.m_harness_deployment_filename)
                    if os.path.exists(self.m_harness_project_filename):
                        os.remove(self.m_harness_project_filename)
                    info("Harness component removed in '%s'" % self.ECOAProject.directory)
                else:
                    error("Harness component already generated in '%s' can't override" % self.ECOAProject.directory)
                    return False

        return True

    def generate_harness_component(self):
        info("=============== GENERATE HARNESS COMPONENT\n")
        harness_generate(self)

    def parse_config_file(self, config_file_path: str):
        info("=============== PARSER CONFIG")
        schema_root = etree.XML('''\
        <xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema">
            <xsd:element name="asctg" type="ASCTG" />
            <xsd:complexType name="ASCTG">
                <xsd:all>
                    <xsd:element name="components" type="ComponentInstance" />
                </xsd:all>
            </xsd:complexType>
            <xsd:complexType name="ComponentInstance">
                <xsd:sequence>
                    <xsd:element maxOccurs="unbounded" name="componentInstance" type="xsd:string" />
                </xsd:sequence>
            </xsd:complexType>
        </xsd:schema>
        ''')
        if os.path.exists(config_file_path):
            # Validate configuration file
            try:
                schema = etree.XMLSchema(schema_root)
                doc = etree.parse(config_file_path)
                schema.assertValid(doc)
                for item in doc.findall("components/componentInstance"):
                    self.harness_components.append(item.text)
                info("Parse from input: %s" % config_file_path)
                info("Harness components: %s" % ', '.join(self.harness_components))
                info("=============== Completed\n\n")
                return True
            except etree.XMLSyntaxError as err:
                error("Syntax error from input: %s\n%s" % (config_file_path, err))
            except etree.DocumentInvalid as err:
                error("Invalid file from input: %s\n%s" % (config_file_path, err))
        else:
            error("Input file '%s' doesn't exists\n" % (config_file_path))

        info("=============== Completed\n\n")
        return False
