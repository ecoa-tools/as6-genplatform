# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

"""
    ECOA-GENPLATFORM - Ecoa Platform Generator
"""

import os
import sys
import argparse
import traceback

from ecoa._version import ecoa_std_version
from ecoa_genplatform.ecoa_generate_config import ECOA_Generate_Config

from ecoa_tools.generator.pattern_files_parser import parse_type_pattern_files
from ecoa_tools.generator.type_functions_generator import generate_compare_types,  generate_zeroise_types
from ecoa_tools.generator.encapsulation_functions_generator import encaps_functions_generate


def parse_args():
	""" Parse genplatform arguments """

	cmd_parser = argparse.ArgumentParser(description="Generate ECOA modules. " +
										"this program generate an LDP ECOA platform described by the project file.\n" +
										"ECOA standard version : {}".format(ecoa_std_version))
	cmd_parser.add_argument('-p', '--project', required=True,
							help="Path to the ECOA project file")
	cmd_parser.add_argument('-k', '--checker', required=True,
							help="Path to the ECOA XML Validation Tool")
	cmd_parser.add_argument('-o', '--output',
							help="Path to the output directory (supersedes the project <outputDirectory/> field)")
	cmd_parser.add_argument('-f', '--force', action='store_true', default=False,
							help="Overwrite the existing elements")
	cmd_parser.add_argument('-g', '--debug', action='store_true', default=False,
							help="Compile with debug informations")
	cmd_parser.add_argument('-c', '--coverage', action='store_true', default=False,
							help="Compile with coverage informations")
	cmd_parser.add_argument('-v', '--verbose', type=int, choices=range(5), default=3,
							help="Verbosity level: 0 = Critical, 4 = Debug")
	cmd_parser.add_argument('-u', '--userid', dest='instance_index', type=int, choices=range(10), default=0,
                        help="User index for multiple instances")

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
	file_log_dir = "logs"

	Global_ECOA = ECOA_Generate_Config(working_directory, arguments.project,
									   index=arguments.instance_index,
									   verbosity=arguments.verbose)

	try:
		# Set Output directory
		if not Global_ECOA.parse_output(arguments.output, xsd_directory):
			# No Output directory found
			Global_ECOA.end()
			sys.exit(1)

		# Call external Ecoa Xml Validation Tool
		if not Global_ECOA.do_external_validation(arguments.checker, arguments.project):
			# ECOA Xml Validation failed exit
			Global_ECOA.end()
			sys.exit(1)

		# Build and re-validate the model (without logging)
		Global_ECOA.do_validation(xsd_directory)

		# Generate ECOA platform
		Global_ECOA.generate(file_log_dir, arguments.force, arguments.debug, arguments.coverage)

		# Generate external tools files
		parse_type_pattern_files(Global_ECOA.types_output_dir, Global_ECOA.libraries)
		generate_compare_types(Global_ECOA.types_output_dir, Global_ECOA.libraries, arguments.force)
		generate_zeroise_types(Global_ECOA.types_output_dir, Global_ECOA.libraries, arguments.force)
		encaps_functions_generate("", Global_ECOA.component_implementations, arguments.force)

	except Exception as e:
		Global_ECOA.end()
		print("Unexpected error:", sys.exc_info()[0], " ", str(e))
		print(traceback.format_exc())
		sys.exit(1)

	Global_ECOA.end()
	sys.stdout.flush()
	sys.exit(0)
