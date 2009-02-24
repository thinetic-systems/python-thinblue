# -*- coding: UTF-8 -*-


from subprocess import Popen, PIPE, STDOUT
import threading

import thinblue.logger as lg
import thinblue.config
import thinblue.db

import time
import os

def findservices_lightblue(address):
    import lightblue
    services={'address':address, 'obex_push_channel':None}
    _services=lightblue.findservices(address)
    for service in _services:
        #lg.debug("found service=%s"%str(service), __name__ )
        # service is like ('00:00:00:00:00:00', 4, 'OBEX Object Push')
        if "OBEX Object Push" in service:
            lg.debug("Found OBEX CHANNEL using LIGHBLUE '%s'" %str(service) , __name__)
            services['obex_push_channel']=service[1]
    
    return services

def findservices_sdptool(address):
    """
     ** buscar canal
    sdptool browse "address"
    
     ** Extracto del valor devuelto
    Service Name: OBEX Object Push
    Service RecHandle: 0x1000b
    Service Class ID List:
      "OBEX Object Push" (0x1105)
    Protocol Descriptor List:
      "L2CAP" (0x0100)
      "RFCOMM" (0x0003)
        Channel: 6
      "OBEX" (0x0008)
    Profile Descriptor List:
      "OBEX Object Push" (0x1105)
        Version: 0x0100
    """
    services={'address':address, 'obex_push_channel':None}
    deviceout = Popen(["sdptool", 
                "-i", thinblue.config.alldevices[thinblue.config.send_device]['dev'], 
                "browse", address], 
                shell=False, stdout=PIPE, stderr=STDOUT, close_fds=True)
    deviceout.wait()
    deviceinfo = deviceout.stdout
    service=None
    while 1:
        line = deviceinfo.readline()
        if not line: break
        lg.debug("SDPTOOL: %s"%line.strip() , __name__)
        
        if line.startswith("Service Name: OBEX Object Push"):
            service="obex_push_channel"
            services[service]=None
            continue
        if service == "obex_push_channel":
            if line.strip().startswith("Channel:"):
                channel=line.split("Channel:")[1].strip()
                services[service]=channel
        if line.startswith("Service Name:"):
            service=None
    return services

def sendfile(address, source):
    
    
    lg.warning("Updating status of '%s' to sending..."%address, __name__)
    sql="UPDATE phones set status='sending' WHERE address='%s';"%address 
    thinblue.db.query(sql)
    
    
    # search channel with lightblue first
    services=findservices_lightblue(address)
    
    #if not services.has_key("obex_push_channel") or services['obex_push_channel'] is None:
    #    lg.warning("Device don't have 'OBEX Object Push', trying with sdptool...", __name__)
    #    services=findservices_sdptool(address)
    
    lg.debug("Device services=%s"%services, __name__)
    
    if not services.has_key("obex_push_channel") or services['obex_push_channel'] is None:
        lg.warning("Device don't have OBEX Object Push", __name__)
        sql="UPDATE phones set status='fail+nopush',date_send='%s' WHERE address='%s';"%(time.asctime(), address )
        thinblue.db.query(sql)
        return
    
    # obexftp --noconn --nopath --uuid=none -b 00:00:00:00:00:00 -B __CHANNEL__ -p ~/Desktop/thinetic.jpg
    
    cmd=["obexftp", "--nopath", "--noconn", "--uuid=none", 
         "--bluetooth", str(address), "--channel", str(services['obex_push_channel']) , 
         "--put", str(source) ]
         
    lg.debug("sendfile() cmd=%s"%" ".join(cmd), __name__ )
    
    sendout = Popen(cmd, shell=False, stdout=PIPE, stderr=STDOUT, close_fds=True)
    sendout.wait()
    sendinfo = sendout.stdout
    
    sendresult="fail"
    while 1:
        line = sendinfo.readline()
        if not line: break
        lg.debug("OBEXFTP: %s"%line.strip() , __name__)
        if line.startswith("Sending"):
            if "failed" in line:
                sendresult="rejected"
            else:
                sendresult="ok"
        #"Disconnecting...failed: disconnect"
        #if line.startswith("Disconnecting"):
        #    if "failed" in line:
        #        sendresult="fail+disconnect"
        
    
    
    # actualizar DB
    if sendresult == "ok":
        # update status send OK
        sql="UPDATE phones set status='send',date_send='%s' WHERE address='%s';"%( time.asctime(), address)
        lg.info("Setting status='send' in device=%s"%address, __name__)
        thinblue.db.query(sql)
    elif sendresult == "rejected":
        # update status send FAIL
        sql="UPDATE phones set status='fail+rejected',date_send='%s' WHERE address='%s';"%(time.asctime(), address )
        lg.warning("Setting status='fail+rejected' in device=%s"%address, __name__)
        thinblue.db.query(sql)
    else:
        # update status send FAIL
        sql="UPDATE phones set status='%s',date_send='%s' WHERE address='%s';"%(sendresult, time.asctime(), address )
        lg.warning("Setting status='%s' in device=%s"%(sendresult, address), __name__)
        thinblue.db.query(sql)
    
    return sendresult


#############################################################################

def main():
    lg.debug("init sending wait 5 secs...", __name__)
    time.sleep(5)
    while not thinblue.is_stoping():
        _file=os.path.join( thinblue.config.file_path , thinblue.config.sendfile )
        
        if thinblue.config.sendfile == "":
            lg.error(" **** No file configured, skipping send... ****", __name__)
            break
        
        if  not os.path.isfile(_file):
            lg.error(" **** file (%s) not found, skipping send... ****"%_file, __name__)
            break

        sql="SELECT address,status from phones WHERE status='pending' LIMIT 0,%s;"%(thinblue.config.concurrent)
        pending=thinblue.db.query(sql)
        #lg.info("Pending (concurrent=%s) send devices=%s"%(thinblue.config.concurrent, pending), __name__)

        # wait 10 secs if no pending sends
        wait=0
        if len(pending) == 0:
            while wait < 10:
                if thinblue.is_stoping():
                    break
                try:
                    time.sleep(1)
                except KeyboardInterrupt:
                    break
                wait=wait+1
            continue
        
        send_threads=[]
        for phone in pending:
            th_send_file = threading.Thread(target = sendfile, args = (phone[0], _file), verbose = thinblue.config.thread_verbose)
            th_send_file.address=phone[0]
            th_send_file.start()
            send_threads.append(th_send_file)
        
        lg.debug("threads started, sleep 2 seconds", __name__)
        time.sleep(2)
        # wait for threads
        lg.debug("waiting for threads...", __name__)
        for th in send_threads:
            lg.debug("thread for address %s join()"%th.address, __name__)
            th.join()
            lg.debug("thread for address %s finished"%th.address, __name__)
        
        lg.debug("all threads finished", __name__)

    lg.info("stopping sending ...", __name__)


