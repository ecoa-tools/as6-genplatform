# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

""" ECOA-EXVT - Ecoa XML Validation Tool
"""

import os, sys, argparse
from ecoa.ecoa_global_config import ECOA_Global_Config
from ecoa._version import ecoa_std_version

def parse_args():
    """ Parse genplatform arguments """

    cmd_parser = argparse.ArgumentParser(description="Generate ECOA modules. " +
                                                     "this program validates an ECOA platform described by the project file.\n"
                                                     "ECOA standard version : {}".format(ecoa_std_version))
    cmd_parser.add_argument('-p', '--project', required=True,
                            help="Path to the ECOA project file")
    cmd_parser.add_argument('-l', '--level', type=int, choices=range(6), default=5,
                            help="ECOA level to validate")
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

    working_directory= os.path.dirname(os.path.abspath(arguments.project))+os.sep
    xsd_directory = os.path.dirname(sys.modules["ecoa"].__file__)+os.sep+"XSD"

    Global_ECOA = ECOA_Global_Config(working_directory, arguments.project,
                                       verbosity=arguments.verbose,
                                       level=arguments.level)

    try:
        # Build and Validate the model
        Global_ECOA.do_parsing(xsd_directory)
        Global_ECOA.build_model(False)

    except Exception as e:
        Global_ECOA.end()
        print("Unexpected error:", sys.exc_info()[0]," ",str(e))
        sys.exit(1)

    l_status = Global_ECOA.end()
    sys.stdout.flush()
    sys.exit(l_status)
