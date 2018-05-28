# -*- coding: UTF-8 -*-
import logging
from logging.handlers import RotatingFileHandler

LOGFILE = "webServer.log"
MAXLOGSIZE = 10*1024*1024 #Bytes
BACKUPCOUNT = 4
FORMAT = \
"%(asctime)s %(levelname)-8s[%(filename)s:%(lineno)d(%(funcName)s)] %(message)s"
LOGLVL = logging.DEBUG

handler = RotatingFileHandler(LOGFILE,
                              mode='a',
                              maxBytes=MAXLOGSIZE,
                              backupCount=BACKUPCOUNT)
formatter = logging.Formatter(FORMAT)
handler.setFormatter(formatter)
#handler.setLevel(LOGLVL) #####刚开始用handler设置日志级别，一直打不出来低于warning级别的日志，问题就在这里

mylog = logging.getLogger()
mylog.setLevel(LOGLVL) #####用LOG类设置级别是OK的
mylog.addHandler(handler)

def info(msg):
    mylog.info(msg)

def error(msg):
    mylog.error(msg)

def debug(msg):
    mylog.debug(msg)

def warning(msg):
    mylog.warning(msg)
