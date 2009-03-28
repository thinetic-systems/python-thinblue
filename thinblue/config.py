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

import os


daemon = True
debug = False
name = "thinblue"
timeout = 8
uid=None


DAEMON_LOG_FILE = "/var/log/thinblue.log"
DAEMON_PID_FILE = "/var/run/thinblue.pid"
DBNAME = "/var/lib/thinblue/database.db"

if os.path.isdir("/.dirs/dev/thinblue"):
    DAEMON_LOG_FILE = "/.dirs/dev/thinblue/thinblue.log"
    DAEMON_PID_FILE = "/.dirs/dev/thinblue/thinblue.pid"
    DBNAME = "/.dirs/dev/thinblue/database.db"


search_device = -1
send_device = -1

stop = False

file_path = "/var/lib/thinblue/files/"
sendfile = "thinetic.jpg"

thread_verbose = False

#print "D: thinblue.config loaded"
