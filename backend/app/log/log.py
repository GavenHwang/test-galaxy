# -*- coding: utf-8 -*-
"""
本文件用例编写日志模块
"""

import os
import logging
from logging.handlers import TimedRotatingFileHandler
from app.settings import settings


class Log(object):
    _flag = None

    def __new__(cls, *args, **kwargs):
        if not cls._flag:
            orig = super(Log, cls)
            cls._flag = orig.__new__(cls)
            logger = logging.getLogger()
            formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
            logger.setLevel(logging.DEBUG)
            logger.propagate = False
            # 日志文件名
            log_file_name = 'plat.log'
            log_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "log", "plat_log", log_file_name)
            if not os.path.exists(os.path.dirname(log_file)):
                os.makedirs(os.path.dirname(log_file))
            # 文件
            file_out = TimedRotatingFileHandler(filename=log_file,  # filename：日志文件名
                                                when='MIDNIGHT',  # when：'MIDNIGHT'-是指过了凌晨12点，就会创建新的日志
                                                interval=1,  # interval是时间间隔
                                                backupCount=50,  # backupCount：是保留日志个数,默认的0是不会自动删除掉日志
                                                encoding='utf-8')
            file_out.namer = lambda name: name.replace("base.log.", "") + ".log"
            file_out.setFormatter(formatter)
            file_out.setLevel(getattr(logging, settings.LOGLEVEL))
            logger.addHandler(file_out)
            # console
            console_out = logging.StreamHandler()
            console_out.setFormatter(formatter)
            console_out.setLevel(getattr(logging, settings.LOGLEVEL))
            logger.addHandler(console_out)

        return cls._flag

    def __init__(self):
        if "log" not in self.__dict__:
            self.log = logging

    def debug(self, msg):
        self.log.debug(msg)
        return True

    def info(self, msg):
        self.log.info(msg)

    def warn(self, msg):
        self.log.warning(msg)

    def error(self, msg):
        self.log.error(msg)


logger = Log()
