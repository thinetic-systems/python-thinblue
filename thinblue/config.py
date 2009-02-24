# -*- coding: UTF-8 -*-

import os


daemon = True
debug = False
name = "thinblue"
timeout = 8


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
sendfile = ""

thread_verbose = False
