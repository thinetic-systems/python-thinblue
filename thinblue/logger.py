# -*- coding: UTF-8 -*-

import logging
import thinblue.config

loglevel=logging.INFO

if thinblue.config.debug:
    loglevel=0


logging.basicConfig(level=loglevel,
                    format='%(asctime)s [%(levelname)s] %(message)s',
                    filename=thinblue.config.DAEMON_LOG_FILE,
                    filemode='a')
#print "logging configured... daemon=%s"%thinblue.config.daemon

def debug(txt, name=thinblue.config.name):
    if thinblue.config.daemon:
        logging.debug("%s:: %s" % (name, txt))
    elif thinblue.config.debug:
        print "D:%s => %s" % (name, txt)

def log(txt, name=thinblue.config.name):
    debug(txt, name)

def info(txt, name=thinblue.config.name):
    if thinblue.config.daemon:
        logging.info("%s:: %s" % (name, txt))
    elif thinblue.config.debug:
        print "I:%s => %s" % (name, txt)

def warning(txt, name=thinblue.config.name):
    if thinblue.config.daemon:
        logging.warning("%s:: %s" %(name, txt))
    else:
        print "W:%s => %s" % (name, txt)

def error(txt, name=thinblue.config.name):
    if thinblue.config.daemon:
        logging.error("%s:: %s" %(name, txt))
    else:
        print "***ERROR**** %s => %s" % (name, txt)

class stderr(object):
    def write(self, data):
        warning(data.replace('\n\n','\n'), "STDERR")

class stdout(object):
    def write(self, data):
        warning(data.replace('\n\n','\n'), "STDOUT")
