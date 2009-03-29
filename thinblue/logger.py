# -*- coding: UTF-8 -*-
##########################################################################
# ThinBlue writen by MarioDebian <mario.izquierdo@thinetic.es>
#
#    Python-ThinBlue              
#
# Copyright (c) 2009 Mario Izquierdo <mario.izquierdo@thinetic.es>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
###########################################################################

import logging
import thinblue.config

loglevel=logging.INFO

if thinblue.config.debug:
    loglevel=0


logging.basicConfig(level=loglevel,
                    format='%(asctime)s [%(levelname)s] %(message)s',
                    filename=thinblue.config.DAEMON_LOG_FILE,
                    filemode='a')
__logger=logging.getLogger()

def setloglevel():
    global loglevel
    if thinblue.config.debug:
        loglevel=logging.DEBUG
    __logger.setLevel(loglevel)
    


def debug(txt, name=thinblue.config.name):
    if thinblue.config.daemon:
        setloglevel()
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
        if data == '\n': return
        warning(data.replace('\n\n','\n'), "STDERR")

class stdout(object):
    def write(self, data):
        if data == '\n': return
        warning(data.replace('\n\n','\n'), "STDOUT")
