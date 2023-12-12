# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

""" logs module """

import logging

class callcounted(object):
    """Decorator to determine number of calls for a method"""

    def __init__(self,method):
        self.method=method
        self.counter=0

    def __call__(self,*args,**kwargs):
        self.counter+=1
        return self.method(*args,**kwargs)

def init_logs(flag):
    """ Initialize the logging module """

    if flag == 0:
        level = logging.CRITICAL
    elif flag == 1:
        level = logging.ERROR
    elif flag == 2:
        level = logging.WARNING
    elif flag == 3:
        level = logging.INFO
    elif flag == 4:
        level = logging.DEBUG
    else:
        level = logging.NOTSET

    logging.basicConfig(format='%(message)s', level=level)
    logging.error = callcounted(logging.error)
    logging.warning = callcounted(logging.warning)
    logging.critical = callcounted(logging.critical)


def debug(string):
    """ Print log """
    logging.debug("DEBUG   |"+string)

def info(string):
    """ Print log """
    logging.info("INFO    |"+string)

def warning(string):
    """ Print log """
    logging.warning("WARNING |"+string)

def error(string):
    """ Print log """
    logging.error("ERROR   |"+string)

def critical(string):
    """ Print log """
    logging.critical("CRITICAL|"+string)

def logger_resume():
    print("End with : ")
    print(" - "+str(logging.critical.counter) + " critical messages")
    print(" - "+str(logging.error.counter) + " error messages")
    print(" - "+str(logging.warning.counter) + " warning messages")

    if logging.error.counter != 0 or logging.critical.counter != 0:
        return 1
    else:
        return 0
