# -*- coding: UTF-8 -*-
##########################################################################
# ThinBlueWeb writen by MarioDebian <mario.izquierdo@thinetic.es>
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


DEV_PATH="/dev/disk/by-label/"
DEV_LABEL="thinblue"

from subprocess import Popen, PIPE, STDOUT
import threading


import thinblue.logger as lg
import thinblue.config
import thinblue.db

import sys
import time
import os
import glob
import shutil

WAIT=2

def __exe_cmd(cmd):
    executing=True
    _cmd=cmd.split()
    out = Popen(_cmd, shell=False, stdout=PIPE, stderr=STDOUT, close_fds=True)
    out.wait()
    sendinfo = out.stdout
    while executing:
        line = sendinfo.readline()
        if not line:
            executing=False
        if line.strip() == "": continue
        lg.debug("exe_cmd: %s"%line.strip() , __name__)

def exe_cmd(cmd):
    lg.debug("exe_cmd('%s')"%cmd, __name__)
    try:
        __exe_cmd(cmd)
    except Exception, err:
        lg.error("exe_cmd() Exception cmd='%s' err='%s'" %(cmd, err), __name__ )

def init_beep():
    exe_cmd("rmmod snd-pcsp")
    exe_cmd("modprobe pcspkr")

def beep_error():
    # 5 short beeps
    exe_cmd("/usr/bin/beep -r 5 -l 100")

def beep_ok():
    # 2 long beeps
    exe_cmd("/usr/bin/beep -f 1000 -r 2 -l 500")

def main():
    DEV=os.path.join(DEV_PATH, DEV_LABEL)
    init_beep()
    lg.debug("init update_device wait %s secs..."%(WAIT*6), __name__)
    time.sleep(WAIT*6)
    while not thinblue.is_stoping():
        # search for DEVICE
        if not os.path.exists(DEV):
            lg.debug(" update_device no dev=%s found..."%(DEV), __name__)
            time.sleep(WAIT)
            continue
        ########################################################################
        # mount
        exe_cmd("mkdir -p /mnt/thinblue")
        exe_cmd("mount %s /mnt/thinblue" %DEV)
        
        # search for update folder
        if not os.path.isdir("/mnt/thinblue/update"):
            # umount and wait again
            exe_cmd("umount /mnt/thinblue")
            beep_error()
            time.sleep(WAIT)
            continue
        
        # we have a update folder
        files=glob.glob("/mnt/thinblue/update/*")
        lg.debug("main() files=%s"%files, __name__)
        if len(files) != 1:
            # have 0 or more than 1 files, exiting....
            exe_cmd("umount /mnt/thinblue")
            beep_error()
            continue
        
        # copy in thinblue dir
        shutil.copy(files[0], thinblue.config.THINBLUE_DIR)
        exe_cmd("umount /mnt/thinblue")
        
        # configure thinblue database
        filename=os.path.basename(files[0])
        thinblue.db.query("UPDATE config set sendfile='%s', stop='2'" %(filename))
        
        # resend files
        thinblue.db.query("UPDATE phones set status='seen1', date_send=''")
        beep_ok()
        
        # wait WAIT*6 seconds to extract pendrive
        time.sleep(WAIT*6)

    lg.debug("update_device STOP stopping detected....", __name__)



if __name__ == '__main__':
    thinblue.config.debug=True
    thinblue.config.daemon=False
    #exe_cmd("/usr/bin/beep -f 1000 -r 2 -l 500")
    lg.info("running", __name__)
    main()
