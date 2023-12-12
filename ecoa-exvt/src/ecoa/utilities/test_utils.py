# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

import os
import re
import shutil
import difflib
import pytest_check as check
from ecoa.utilities.process import execute


def save_to(file, content):
    if not content:
        content = ""
    else:
        content = content.decode("utf-8")
    with open(file, 'w') as f:
        f.write(content)


def exclude_date_and_PARSEC(line: str):
    if 'date:' in line or 'Generated by : LDP' in line:
        return True
    return False


def filter_platform_CMakeLists(line: str):
    if ('add_executable(platform' in line
            or 'target_include_directories(platform' in line
            or '5-Integration/inc-gen' in line
            or '5-Integration/inc' in line):
        return True
    return False


def find_patterns(file, patterns):
    l_nb_occ = [0]*len(patterns)
    with open(file, "r") as lines:
        for c_line in lines:
            for c_idx, c_pattern in enumerate(patterns):
                if re.search(c_pattern, c_line):
                    l_nb_occ[c_idx] += 1
                    break
    for c_item in l_nb_occ:
        if c_item == 0:
            return False
    return True


def dont_find_patterns(file, patterns):
    with open(file, "r") as lines:
        for c_line in lines:
            for c_pattern in patterns:
                if re.search(c_pattern, c_line):
                    return False
    return True


class RunTool:
    def __init__(self, working_directory, project, testcase, saveOutput=True, saveError=True, output_suffix=""):
        self.m_output = os.path.join(working_directory, "output", testcase)
        self.m_project_file = os.path.join(self.m_output, "%s.project.xml" % project)
        self.m_config_file = os.path.join(self.m_output, "%s.config.xml" % project)
        self.m_data = os.path.join(working_directory, "data", project)
        self.m_cmake_config = os.path.join(working_directory, "data", "cmake_config.cmake")
        self.m_generated = os.path.join(working_directory, "generated", testcase)
        self.m_saveOutput = saveOutput
        self.m_saveError = saveError
        self.m_parsing_out = os.path.join(self.m_output, "parsing%s.out" % output_suffix)
        self.m_parsing_err = os.path.join(self.m_output, "parsing%s.err" % output_suffix)
        self.m_root_path = os.path.dirname(os.path.dirname(working_directory))

    def copy_dir(self):
        if os.path.exists(self.m_output):
            shutil.rmtree(self.m_output)
        shutil.copytree(
            src=self.m_data,
            dst=self.m_output)

    def run(self, command, removeEnv=True):
        # Copy environment
        if removeEnv:
            self.copy_dir()

        # Run generator
        code, output, error = execute(command)

        # Stores output and error
        if self.m_saveOutput:
            save_to(self.m_parsing_out, output)
        if self.m_saveError:
            save_to(self.m_parsing_err, error)

        return code, output, error

    def validate(self, filesList):
        for c_file in filesList:
            lines1 = open(os.path.join(self.m_generated, c_file), "r").readlines()
            lines1 = list(map(lambda a: str(a).replace("%ROOT_PATH%", self.m_root_path), lines1))
            lines1[:] = filter(lambda line: not exclude_date_and_PARSEC(line), lines1)
            if '6-Output/platform/CMakeLists.txt' == c_file:
                lines1[:] = filter(lambda line: not filter_platform_CMakeLists(line), lines1)

            lines2 = open(os.path.join(self.m_output, c_file), "r").readlines()
            lines2[:] = filter(lambda line: not exclude_date_and_PARSEC(line), lines2)
            if '6-Output/platform/CMakeLists.txt' == c_file:
                lines2[:] = filter(lambda line: not filter_platform_CMakeLists(line), lines2)

            contextDiffSeq = difflib.unified_diff(lines1, lines2, n=0, lineterm="")
            contextDiffList = list(contextDiffSeq)
            check.equal('\n'.join(contextDiffList), "", "'{}' files differ".format(c_file))

    def compile(self, cflags=None, cxxflags=None):
        # Check dependencies variable
        l_deps_path = os.getenv("ECOA_DEPS_DIR")
        assert l_deps_path is not None, "Env variable ECOA_DEPS_DIR not defined"

        # Run cmake
        l_cmd = "cmake3 -DLOG4CPLUS_DIR={0} -DAPR_DIR={0} -C {1}".format(l_deps_path, self.m_cmake_config)
        if cflags:
            l_cmd += " -DUSER_CMAKE_C_FLAGS=\"{0}\"".format(cflags)
        if cxxflags:
            l_cmd += " -DUSER_CMAKE_CXX_FLAGS=\"{0}\"".format(cxxflags)
        l_cmd += " {0}/6-Output/CMakeLists.txt".format(self.m_output)
        code, _, _ = self.run(l_cmd, removeEnv=False)

        # Run make
        if code == 0:
            l_cmd = "make -C {0}/6-Output all".format(self.m_output)
            code, _, _ = self.run(l_cmd, removeEnv=False)

        return code
