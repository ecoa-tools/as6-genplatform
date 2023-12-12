# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

"""
    generate log properties file for a new logger name
"""

import os
from ..force_generation import file_need_generation


def generate_log_properties(log_properties_dir, logger_name, log_file_path, force_flag):
    # log4cplus conf file
    generate_properties_file(log_properties_dir, logger_name, log_file_path, force_flag)

    # zlog conf file
    generate_zlog_file(log_properties_dir, logger_name, log_file_path, force_flag)


def generate_properties_file(log_properties_dir, logger_name, log_file_path, force_flag):
    """@TODO Function docstring"""
    log_properties_file = log_properties_dir + os.sep + "log_" + logger_name + ".properties"

    if not file_need_generation(log_properties_file,
                                force_flag,
                                log_properties_file + " already exists for %s" % logger_name):
        return

    file = open(log_properties_file, 'w')

    text = ""
    text += "log4cplus.rootLogger=TRACE \n"
    text += "log4cplus.logger." + logger_name + "=TRACE," + logger_name + "_appender\n"
    text += "log4cplus.appender." + logger_name + "_appender=log4cplus::RollingFileAppender\n"
    text += "log4cplus.appender." + logger_name + "_appender.File=" + log_file_path + os.sep \
            + "log_" + logger_name + ".log\n"
    text += "log4cplus.appender." + logger_name + "_appender.CreateDirs=true\n"
    text += "log4cplus.appender." + logger_name + "_appender.Append=false\n"
    text += "log4cplus.appender." + logger_name + "_appender.MaxBackupIndex=10\n"
    text += "log4cplus.appender." + logger_name + "_appender.MaxFileSize=3MB\n"
    text += "log4cplus.appender." + logger_name + "_appender.layout=log4cplus::PatternLayout\n"
    text += "log4cplus.appender." + logger_name + "_appender.layout.ConversionPattern=%m%n"

    print(text, file=file)
    file.close()


def generate_zlog_file(log_properties_dir, logger_name, log_file_path, force_flag):
    """@TODO Function docstring"""
    log_properties_file = log_properties_dir + os.sep + "log_" + logger_name + ".zlog"

    if not file_need_generation(log_properties_file,
                                force_flag,
                                log_properties_file + " already exists for %s" % logger_name):
        return

    file = open(log_properties_file, 'w')

    text = ""
    text += "[formats]\n"
    text += "simple = \"%m%n\"\n"
    text += ""
    text += "[rules]\n"
    text += logger_name + ".DEBUG    \"" + \
            os.path.join(".", log_file_path, "log_" + logger_name + ".log") + "\"; simple\n"
    if "main_PF" not in logger_name:
        text += logger_name + "_PF.DEBUG    \"" \
                + os.path.join(".", log_file_path, "log_" + logger_name + "_PF.log") + "\"; simple\n"

    print(text, file=file)
    file.close()
