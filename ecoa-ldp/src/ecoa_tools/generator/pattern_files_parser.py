# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

import re
import os
from collections import OrderedDict
from ecoa.utilities.logs import *


"""
###############################################
###  Parser for pattern files
###############################################
"""
def _find_prefix(string):
    prefix = None
    regex_prefix = r"(?<=PREFIX)[\s]*=[\s]*[^-\s]+"
    matches = re.search(regex_prefix, string)
    if matches != None:
        prefix = matches.group(0).replace(' ','').replace('=','')
    return prefix

def _find_suffix(string):
    suffix = None
    regex_suffix = r"(?<=SUFFIX)[\s]*=[\s]*[^-\s]+"
    matches = re.search(regex_suffix, string)
    if matches != None:
        suffix = matches.group(0).replace(' ','').replace('=','')
    return suffix

def _find_epsilon(string):
    epsilon = None
    regex_epsilon = r"(?<=EPSILON)[\s]*=[\s]*((\+|-)?[0-9]*\.?[0-9]*((e|E)-[0-9]{1,2})?)"
    matches = re.search(regex_epsilon, string)
    if matches != None:
        epsilon = matches.group(1)
    return epsilon


def parse_type_pattern_files(types_directory, libraries):
    """Parse pattern files if each libraries

    find suffix and prefix for compare and zeroise function. And set thes value in each library object

    Args:
        types_directory  (str) : The types directory (0-Types)
        libraries        (dict): dictionary of all (:class:`~ecoa.models.library.Library`)
    """
    for lib,_ in libraries.values():
        comp_pattern_fname = os.path.join(types_directory, "pattern", lib.name+"_pattern_comp.txt")
        if os.path.exists(comp_pattern_fname):
            info("compare pattern file found for library "+lib.name)
            comp_pattern_file=open(comp_pattern_fname)

            for line in comp_pattern_file:
                prefix = _find_prefix(line)
                if prefix != None:
                    lib.comp_prefix=prefix
                    debug(lib.name+" prefix : \'"+prefix+"\'")
                    continue

                suffix = _find_suffix(line)
                if suffix != None:
                    lib.comp_suffix=suffix
                    debug(lib.name+" suffix : \'"+suffix+"\'")

                # find epsilon
                epsilon = _find_epsilon(line)
                if epsilon != None:
                    lib.epsilon=epsilon
                    debug(lib.name+" epsilon : \'"+epsilon+"\'")


            comp_pattern_file.close()
        else:
            info("compare pattern file not found for library "+lib.name)

        init_pattern_fname = os.path.join(types_directory, "pattern", lib.name+"_pattern_init.txt")
        if os.path.exists(init_pattern_fname):
            info("init pattern file found for library "+lib.name)
            init_pattern_file=open(init_pattern_fname)

            for line in init_pattern_file:
                prefix = _find_prefix(line)
                if prefix != None:
                    lib.zeroise_prefix=prefix
                    debug(lib.name+" prefix : \'"+prefix+"\'")
                    continue

                suffix = _find_suffix(line)
                if suffix != None:
                    lib.zeroise_suffix=suffix
                    debug(lib.name+" suffix : \'"+suffix+"\'")
            init_pattern_file.close()
        else:
            info("init pattern file not found for library "+lib.name)


def parse_component_pattern_file(component_directory):
    """Find prefix for encapsulated functions

    Return:
        (str): prefix string
    """

    file_name=os.path.join(component_directory, "pattern", "pattern_encaps.txt")
    prefix = None
    if(os.path.exists(file_name)):
        encaps_file = open(file_name)
        for line in encaps_file:
            prefix = _find_prefix(line)
            if prefix != None:
                break
        encaps_file.close()
    if prefix == None:
        prefix = "LDP"
    debug("encaps prefix : \'"+prefix+"\'")

    return prefix



def parse_module_pattern_file(mod_impl_directory, mod_impl, mod_type):
    """Parse pattern files for module

    Find macros and saved code in dictionary

    Args:
        mod_impl_directory  (str):The module implementation directory
        mod_impl            (Module_Implementation): The module implementation
        mod_type            (Module_Type): The module type

    Return:
        (dict): dictionary that contains : macro_string => code_string
    """
    file_name = os.path.join(mod_impl_directory, 'pattern', mod_impl.name+"_pattern.c")

    pattern_dict=OrderedDict()
    if(os.path.exists(file_name)):
        file = open(file_name)
        macro_start = re.compile('^\/\*\*(?![\s]*END\sOF\s)([a-zA-Z0-9_\s]*)\*\*\/[\s]*$')
        macro_stop = re.compile('^\/\*\*[\s]*END\sOF[\s]+([a-zA-Z0-9_\s]*)\*\*\/[\s]*$')

        macro_content = ""
        macro_name = ""
        macro_started=False

        for line in file:
            if macro_started:
                match_stop = macro_stop.search(line)
                if match_stop != None:
                    if match_stop.group(1).strip() != macro_name:
                        error("["+mod_impl.name+"_pattern.c] waitting for \'"+macro_name+"\'. But found \'"+match_stop.group(1)+"\'")
                    else:
                        # saving macro_content in dict
                        pattern_dict[macro_name] = macro_content
                    macro_started = False
                    macro_content = ""
                else:
                    #saved line string
                    macro_content+=line
            else:
                match_start = macro_start.search(line)
                if match_start != None:
                    # start saving string
                    macro_content = ""
                    macro_name = match_start.group(1).strip()
                    macro_started = True

                    if macro_name in pattern_dict:
                        warning("["+mod_impl.name+"_pattern.c] Multiple definition of macro : \'"+ macro_name+"\'")

        file.close()

        parse_module_pattern_file_h(mod_impl_directory, mod_impl, pattern_dict)

    return pattern_dict

def parse_module_pattern_file_h(mod_impl_directory, mod_impl, pattern_dict):
    """Parse pattern header file for user code in module

    File pattern_dict with the key `USER CODE HEADER`

    Args:
        mod_impl_directory  (str): The module implementation directory
        mod_impl            (Module_Implementation): The module  implementation
        pattern_dict        (dict): The pattern dictionary
    """
    file_name = os.path.join(mod_impl_directory, 'pattern', mod_impl.name+'_pattern.h')

    header_str = ""
    if(os.path.exists(file_name)):
        with open(file_name) as file:
            macro_start = re.compile('^\/\*\*(?![\s]*END\sOF\s)[\s]*USER[\s]+CODE[\s]+HEADER[\s]*\*\*\/[\s]*$')
            macro_stop = re.compile('^\/\*\*[\s]*END\sOF[\s]+USER[\s]+CODE[\s]+HEADER[\s]*\*\*\/[\s]*$')
            macro_started=False
            header_str="\n"
            for line in file:
                if macro_started:
                    if macro_stop.search(line) != None:
                        # stop macro found
                        break
                    else:
                        # save line
                        header_str += line
                else:
                    # search for macro start
                    macro_started = (macro_start.search(line) != None)


    if header_str != "":
        pattern_dict["USER CODE HEADER"] = header_str



