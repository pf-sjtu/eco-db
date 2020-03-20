# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 09:25:37 2020

@author: PENG Feng
@email:  im.pengf@outlook.com
"""


class Logger:
    CBlACK = "\033[30m"
    CRAD = "\033[31m"
    CGREEN = "\033[32m"
    CYELLOW = "\033[33m"
    CBLUE = "\033[34m"
    CPURPLE = "\033[35m"
    CDGREEN = "\033[36m"
    CWHITE = "\033[37m"

    FAIL = "\033[91m"
    HIGH = "\033[92m"
    WARNING = "\033[93m"
    OKBLUE = "\033[94m"
    HEADER = "\033[95m"
    ENDC = "\033[0m"

    @staticmethod
    def log_normal(info, att=""):
        print(Logger.OKBLUE + info + Logger.ENDC, att)

    @staticmethod
    def log_high(info, att=""):
        print(Logger.HIGH + info + Logger.ENDC, att)

    @staticmethod
    def log_warn(info, att=""):
        print(Logger.WARNING + info + Logger.ENDC, att)

    @staticmethod
    def log_fail(info, att=""):
        print(Logger.FAIL + info + Logger.ENDC, att)


if __name__ == "__main__":
    Logger.log_normal("This is a normal message!", "test")
    Logger.log_high("This is a high-light message!")
    Logger.log_warn("This is a warning message!")
    Logger.log_fail("This is a fail message!")
    Logger.log_warn("WARNING:", "no more recent data available in the period.")
