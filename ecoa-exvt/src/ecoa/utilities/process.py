# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

import os, subprocess

def execute(cmd, cwd=None):
    """
    Execute given command in given working directory
    If the command takes more than given timeout, return an error code
    Returns the process exit code as well as stdout and stderr
    """
    if not cwd:
        cwd = os.getcwd()
    proc = subprocess.Popen(cmd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True, cwd=cwd, preexec_fn=os.setsid)
    output, error = proc.communicate()
    code = proc.returncode
    return code, output, error
