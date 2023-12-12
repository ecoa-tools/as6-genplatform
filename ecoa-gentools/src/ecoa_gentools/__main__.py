# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

""" ECOA-GENTOOLS - Ecoa Platform Generation Tools
"""

import os, sys, argparse
from ecoa_gentools.ecoa_tools_config import ECOA_Gentools_Config
from ecoa_gentools.comparator.comparator import models_comparator


def parse_args():
	""" Parse gentools arguments """

	# create parser which is common by all commands
	common_parser = argparse.ArgumentParser(description="Generate ECOA modules. "+
			"Without subcommand, this program generate an LDP ECOA platform described by the configuration file.",
			add_help=False)
	common_parser.add_argument('-v', '--verbose', type=int, choices=range(5), default=3,
							   help="Verbosity level: 0 = Critical, 4 = Debug")
	common_parser.add_argument('config', metavar='config', type=str, nargs=1,
							   help="Configuration filename. Described an ECOA platform which should be generated.")

	# command parser
	cmd_parser = argparse.ArgumentParser()
	subparsers = cmd_parser.add_subparsers(description="Gentools sub-commands",
										   dest="sub_cmd")
	## ECOA model comparator
	diff_parser = subparsers.add_parser("diff", description="Compare 2 ECOA projects",
										parents=[common_parser],# add_help=False,
										help="Compare 2 ECOA projects")
	diff_parser.add_argument("config2", metavar='config2', type=str, nargs=1,
							 help="Configuration filename. Describe another ECOA platform")

	## Binary descriptor generator
	binary_parser = subparsers.add_parser("bin-desc", description="Generate bin-desc files", parents=[common_parser],
										  help="Generate bin-desc.xml files for every module implementation")
	binary_parser.add_argument('--c-compiler', dest='c_compiler',
							   type=str, action="store", default="gcc",
							   help="Define the C compiler")
	binary_parser.add_argument('--cpp-compiler', dest='cpp_compiler',
							   type=str, action="store", default="g++",
							   help="Define the C++ compiler")
	binary_parser.add_argument('--c-flags', dest='c_flags',
							   type=str, action="store", default="",
							   help="Define the C flags")
	binary_parser.add_argument('--cpp-flags', dest='cpp_flags',
							   type=str, action="store", default="",
							   help="Define the C++ flags")

	# return command parser
	return cmd_parser.parse_args()


def main() -> None:
	"""The entry point."""
	arguments = parse_args()
	working_directory= os.path.dirname(os.path.abspath(arguments.config[0]))+os.sep
	xsd_directory = os.path.dirname(sys.modules["ecoa"].__file__)+os.sep+"XSD"

	Global_ECOA = ECOA_Gentools_Config(working_directory, arguments.config[0],
									   verbosity=arguments.verbose)

	try:
		# Set Output directory
		if not Global_ECOA.parse_output(arguments.output, xsd_directory):
			# No Output directory found
			Global_ECOA.end()
			sys.exit(1)

		# Build and Validate the model
		Global_ECOA.do_parsing(xsd_directory)
		Global_ECOA.build_model()

		if arguments.sub_cmd == "bin-desc":
			# generate binary descriptor file (and files for modules and types)
			bin_desc_options=(arguments.c_compiler,
							  arguments.cpp_compiler,
							  arguments.c_flags,
							  arguments.cpp_flags)

			Global_ECOA.generate(arguments.force, bin_desc_options)
		elif arguments.sub_cmd == "diff":
			# find difference between 2 ECOA project

			# make second ecoa model
			Global_ECOA_2 = ECOA_Gentools_Config(working_directory, arguments.config2[0],
												 arguments.verbose)
			Global_ECOA_2.do_parsing(xsd_directory)
			Global_ECOA_2.build_model()

			# make comparaison
			models_comparator(Global_ECOA, Global_ECOA_2)
		else:
			print("Invalid sub-command:", arguments.sub_cmd)
			sys.exit(1)

	except Exception as e:
		Global_ECOA.end()
		print("Unexpected error:", sys.exc_info()[0]," ",str(e))
		sys.exit(1)


	Global_ECOA.end()
	sys.stdout.flush()
	sys.exit(0)
