# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

""" ECOA-ASCTG - Application Software Component Test Generator.
"""

import os
import sys
import argparse
from ecoa._version import ecoa_std_version
from ecoa_asctg.ecoa_harness_config import ECOA_Harness_Config


def parse_args():
    """ Parse genplatform arguments """

    cmd_parser = argparse.ArgumentParser(description="Generate ECOA modules. " +
                        "this program generate a single ECOA HARNESS component used to test ECOA componnents.\n" +
                        "ECOA standard version : {}".format(ecoa_std_version))
    cmd_parser.add_argument('-c', '--config', required=True,
                            help="Path to the Config file")
    cmd_parser.add_argument('-p', '--project', required=True,
                            help="Path to the ECOA project file")
    cmd_parser.add_argument('-k', '--checker', required=True,
                            help="Path to the ECOA XML Validation Tool")
    cmd_parser.add_argument('-o', '--output',
                            help="Path to the output directory (supersedes the project <outputDirectory/> field)")
    cmd_parser.add_argument('-f', '--force', action='store_true', default=False,
                            help="Overwrite the existing elements")
    cmd_parser.add_argument('-v', '--verbose', type=int, choices=range(5), default=3,
                            help="Verbosity level: 0 = Critical, 4 = Debug")
    # return command parser
    return cmd_parser.parse_args()


def main() -> None:
    """The entry point."""
    try:
        arguments = parse_args()
    except SystemExit as e:
        sys.exit(e.code != 0)

    working_directory = os.path.dirname(os.path.abspath(arguments.project))+os.sep
    xsd_directory = os.path.dirname(sys.modules["ecoa"].__file__)+os.sep+"XSD"

    Global_ECOA = ECOA_Harness_Config(working_directory, arguments.project,
                                      verbosity=arguments.verbose)

    try:
        # Set Output directory
        if not Global_ECOA.parse_output(arguments.output):
            # No Output directory found
            Global_ECOA.end()
            sys.exit(1)

        # Parsing ASCTG configuration file
        if not Global_ECOA.parse_config_file(arguments.config):
            # Config file parsing failed exit
            Global_ECOA.end()
            sys.exit(1)

        # Call external ECOA Xml Validation Tool
        if not Global_ECOA.do_external_validation(arguments.checker, arguments.project):
            # ECOA Xml Validation failed exit
            Global_ECOA.end()
            sys.exit(1)

        # Copy project in output directory if needed and checks if generation is possible
        if not Global_ECOA.copy_and_check_project(xsd_directory, arguments.force):
            # Check of project failed
            Global_ECOA.end()
            sys.exit(1)

        # Build and re-validate the model (without logging)
        Global_ECOA.do_validation(xsd_directory, False)

        # Generate harness component
        Global_ECOA.generate_harness_component()

    except Exception as e:
        Global_ECOA.end()
        print("Unexpected error:", sys.exc_info()[0], " ", str(e))
        sys.exit(1)

    Global_ECOA.end()
    sys.stdout.flush()
    sys.exit(0)
