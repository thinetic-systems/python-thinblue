__all__=['logger', 'config', 'search', 'obexftpsend', 'send', 'db', 'daemonize']

import thinblue.config
import thinblue.logger as lg

import os

def init():
    import thinblue.db
    #lg.debug("loading settings from database", __name__)
    
    
    sendfile=thinblue.db.query("SELECT sendfile from config;")[0][0]
    thinblue.config.sendfile=sendfile
    
    file_path=thinblue.db.query("SELECT file_path from config;")[0][0]
    thinblue.config.file_path=file_path
    
#    debug=thinblue.db.query("SELECT debug from config;")[0][0]
#    if debug > 0:
#        thinblue.config.debug=True
#    else:
#        thinblue.config.debug=False
    
    timeout=thinblue.db.query("SELECT timeout from config;")[0][0]
    thinblue.config.timeout=int(timeout)
    
    concurrent=thinblue.db.query("SELECT concurrent from config;")[0][0]
    thinblue.config.concurrent=int(concurrent)
    
    # set stop to 0
    thinblue.db.query("UPDATE config SET stop=0;")
    thinblue.config.stop=False
    
    #lg.debug("settings loaded", __name__)

def do_stop():
    thinblue.db.query("UPDATE config SET stop=1;")
    thinblue.config.stop=True
    #lg.info("Stopping...", __name__)

def is_stoping(dosql=False):
    if not dosql:
        return thinblue.config.stop
    try:
        stop=thinblue.db.query("SELECT stop from config;")[0][0]
    except Exception, err:
        lg.error("Exception can't read stop status '%s'"%err, __name__)
        return False
    
    if stop == 1:
        return True
    elif stop == 2:
        # reload config
        lg.info("Reloading configuration...", __name__)
        init()
        return False
    else:
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
        sys.exit(1)
    thinblue.config.search_device=1
    thinblue.config.send_device=0
    thinblue.config.alldevices=alldevices
    for dev in alldevices:
        lg.debug("Configuring device '%s' with noauth and nocrypt"%dev['dev'], __name__)
        os.system("hciconfig %s down" %dev['dev'])
        os.system("hciconfig %s up noscan noauth noencrypt" %dev['dev'])
    
    lg.debug("Found 2 Bluetooth devices %s"%alldevices, __name__)
