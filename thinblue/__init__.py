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


import thinblue.config
import thinblue.logger as lg

import os
import pwd

import thinblue.db

def init():
    import thinblue.config
    #try:
    #    uid=pwd.getpwnam("www-data")
    #except KeyError:
    #    print >> sys.stderr, "User www-data not found"
    #    sys.exit(1)
    #thinblue.config.uid=uid[2]
    #lg.debug("www-data userid=%s"%thinblue.config.uid, __name__)
    
    # set rights of database dir
    if not os.path.isdir( os.path.dirname(thinblue.config.DBNAME) ):
        os.mkdir( os.path.dirname(thinblue.config.DBNAME) )
    
    if not os.path.isfile(thinblue.config.DBNAME):
        thinblue.db.create_db()
    
    #os.chown(thinblue.config.DBNAME, uid[2], uid[3])

    
    lg.debug("loading settings from database", __name__)
    
    sendfile=thinblue.db.query("SELECT sendfile from config;")[0][0]
    thinblue.config.sendfile=sendfile
    lg.debug("sendfile=%s"%thinblue.config.sendfile, __name__)
    
    file_path=thinblue.db.query("SELECT file_path from config;")[0][0]
    thinblue.config.file_path=file_path
    lg.debug("file_path=%s"%thinblue.config.file_path, __name__)
    
    timeout=thinblue.db.query("SELECT timeout from config;")[0][0]
    thinblue.config.timeout=int(timeout)
    lg.debug("timeout=%s"%thinblue.config.timeout, __name__)
    
    concurrent=thinblue.db.query("SELECT concurrent from config;")[0][0]
    thinblue.config.concurrent=int(concurrent)
    lg.debug("concurrent=%s"%thinblue.config.concurrent, __name__)
    
    # set stop to 0
    thinblue.db.query("UPDATE config SET stop=0;")
    thinblue.config.stop=False
    
    lg.debug("init() settings loaded", __name__)
    thinblue.db.close()

def do_stop():
    thinblue.db.query("UPDATE config SET stop=1;")
    thinblue.config.stop=True
    #lg.info("Stopping...", __name__)
    thinblue.db.close()

def is_stoping(dosql=False):
    #print "is stopping"
    if not dosql:
        return thinblue.config.stop
    try:
        stop=thinblue.db.query("SELECT stop from config;")[0][0]
    except Exception, err:
        lg.error("Exception can't read stop status '%s'"%err, __name__)
        return False
    
    if stop == 1:
        lg.info("is_stopping() True...", __name__)
        return True
    elif stop == 2:
        # reload config
        lg.info("Reloading configuration...", __name__)
        init()
        return False
    else:
        #lg.info("is_stopping() False...", __name__)
        return False

def load_devices():
    alldevices=[]
    lg.debug("searching for avalaible Bluetooth devices...", __name__)
    from subprocess import Popen, PIPE, STDOUT
    import sys
    devicesout = Popen(["hcitool", "dev"], \
                shell=False, stdout=PIPE, stderr=STDOUT, close_fds=True)
    devicesout.wait()
    devices = devicesout.stdout
    while 1:
        line = devices.readline()
        if not line: break
        if line.startswith("Devices:"): continue
        dev=line.strip().split()
        alldevices.append(  {'dev':dev[0], 'address':dev[1]}  )
    if len(alldevices) != 2:
        lg.error("ERROR: Need 2 Bluetooth devices to work", __name__)
        print >> lg.old_stderr, "ThinBlue error: need 2 Bluetooth devices to work, no starting..."
        sys.exit(1)
    thinblue.config.search_device=1
    thinblue.config.send_device=0
    thinblue.config.alldevices=alldevices
    for dev in alldevices:
        lg.debug("Configuring device '%s' with noauth and nocrypt"%dev['dev'], __name__)
        os.system("hciconfig %s down" %dev['dev'])
        os.system("hciconfig %s up noscan noauth noencrypt" %dev['dev'])
    
    lg.debug("Found 2 Bluetooth devices %s"%alldevices, __name__)

__all__=['logger', 'config', 'search', 'obexftpsend', 'send', 'db', 'daemonize', 'update_device']
