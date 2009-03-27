#!/usr/bin/env python
# -*- coding: UTF-8 -*-
##########################################################################
# Python-ThinBlue writen by MarioDebian <mario.izquierdo@thinetic.es>
#
#    Python-ThinBlue version 0.0.1
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

import os
import sys
import getopt
import time

import threading

import thinblue.config

if "--debug" in sys.argv:
    thinblue.config.debug = True

if "--nodaemon" in sys.argv:
    thinblue.config.debug = True
    thinblue.config.daemon = False
else:
    thinblue.config.daemon = True


if "--help" in sys.argv:
    print """
thinblue
        --start    - start daemon
        --stop     - stop daemon
        --status   - return status (1 running 0 stoped)
        
        --debug    - enable debug logging
        --nodaemon - no fork process
"""
    sys.exit(0)

def drop_privileges():
    #    >>> for u in pwd.getpwall():
    #...   if u[0]=="www-data":
    #...       print u
    #... 
    #('www-data', 'x', 33, 33, 'www-data', '/var/www', '/bin/sh')
    # get www-data user id
    pass


import thinblue
thinblue.init()

import thinblue.logger as lg

def run():
    import thinblue.search
    #import thinblue.send
    import thinblue.obexftpsend
    thinblue.load_devices()
    
    lg.info("init threads...", __name__)
    
    th_search = threading.Thread(target = thinblue.search.main, verbose = thinblue.config.thread_verbose)
    th_search.start()
    
    th_send = threading.Thread(target = thinblue.obexftpsend.main, verbose = thinblue.config.thread_verbose)
    th_send.start()
    
    lg.info("threads started...", __name__)
    
    while not thinblue.is_stoping(dosql = True):
        try:
            time.sleep(2)
        except KeyboardInterrupt:
            lg.info("KeyboardInterrupt, exiting...", __name__)
            break
    thinblue.do_stop()
    lg.info("stopper::exiting... PLEASE WAIT....", __name__)


if __name__ == '__main__':
    try:
        OPTS, ARGS = getopt.getopt(sys.argv[1:], ":hd", ["help", "debug", "start", "stop", "status", "nodaemon"])
    except getopt.error, msg:
        print msg
        print "for command line options use thinblue --help"
        sys.exit(2)
    
    for o, a in OPTS:
        if o == "--start":
            
            if not "--nodaemon" in sys.argv:
                import thinblue.daemonize
                thinblue.daemonize.start_server()
                sys.stderr = lg.stderr()
                sys.stdout = lg.stdout()
            lg.debug("run now", __name__)
            run()
        
        elif o == "--stop":
            # set stoping
            thinblue.do_stop()
            # read PID
            if not os.path.isfile(thinblue.config.DAEMON_PID_FILE):
                sys.exit(0)
            # wait for pid if exists
            pid = open(thinblue.config.DAEMON_PID_FILE, 'r').read().strip()
            print ( " wating for pid %s... "%pid )
            while os.path.isdir("/proc/%s"%pid):
                print ( " wating for pid %s... "%pid )
                time.sleep(0.5)
            os.remove(thinblue.config.DAEMON_PID_FILE)
        
        elif o == "--status":
            pass








