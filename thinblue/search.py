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

import socket
socket.setdefaulttimeout(30)


import bluetooth
from bluetooth.btcommon import BluetoothError
import bluetooth._bluetooth as _bt
import struct

import select

import thinblue.logger as lg
import thinblue.config
import thinblue.db

import time

BLUE_TYPES = ( "Miscellaneous", 
                  "Computer", 
                  "Phone", 
                  "LAN/Network Access point", 
                  "Audio/Video", 
                  "Peripheral", 
                  "Imaging" )

BLUE_SERVICES = ( (16, "positioning"), 
                (17, "networking"), 
                (18, "rendering"), 
                (19, "capturing"),
                (20, "object transfer"), 
                (21, "audio"), 
                (22, "telephony"), 
                (23, "information"))



class Phone(object):
    def __init__(self, address, device_class, name):
        self.name=name
        self.address=address
        self.services=[]
        
        lg.info("Phone: NEW phone device", __name__)
        # populate services
        for bitpos, classname in BLUE_SERVICES:
            if device_class & (1 << (bitpos-1)):
                self.services.append(classname)
                
        if not 'object transfer' in self.services:
            lg.debug("Device '%s' don't have object transfer" %(self.address), __name__)
            return
        
        
        # read from DB to search MAC address
        res=thinblue.db.query("SELECT address,status from phones WHERE address = '%s' ;" %self.address)
        #lg.debug("Phone() res=%s"%res, __name__)
        
        if len(res) > 0:
            if "fail" in res[0][1] or res[0][1] == "send" or res[0][1] == "sending":
                #lg.debug("Phone address (%s) status send/sending or fail (%s) skiping..." %(self.address, res[0]['status']), __name__)
                return
        
            if res[0][1] == "seen1":
                lg.debug("Phone address (%s) in database as seen1, set to pending..." %self.address, __name__)
                thinblue.db.query("UPDATE phones set status='pending' WHERE address='%s'" %self.address)
                return
                
            if res[0][1] == "pending":
                #lg.debug("Phone address (%s) in pending status skiping..." %self.address, __name__)
                return
            
            
        
        
        
        # get device name (by default no search for names)
        #if self.name == '' or self.name is None:
        #    lg.info("looking for name of address='%s'..."%self.address, __name__)
        #    self.name=bluetooth.bluez.lookup_name(self.address)
        #    lg.info("name of address='%s'  found='%s'"%(self.address, self.name) , __name__)
        
        thinblue.db.query("""INSERT INTO phones (address, status, date_search) 
        VALUES ('%s', 'seen1', '%s')""" 
        %(self.address,  time.asctime()   ) )
        
        lg.info("Phone: NEW phone device: %s %s SAVED as seen1" %(self.address, self.services), __name__)


# overwrite _gethcisock

def _gethcisock (device_id = thinblue.config.search_device):
    #lg.debug("_gethcisock() device=%s"%device_id, __name__)
    try:
        sock = _bt.hci_open_dev (device_id)
    except Exception, err:
        #raise BluetoothError ("error accessing bluetooth device")
        lg.warning("Exception: _gethcisock, error='%s'" %err, __name__)
        return None
    return sock

bluetooth.bluez._gethcisock=_gethcisock

class DiscoverAndSend(bluetooth.DeviceDiscoverer):
    def pre_inquiry(self):
        lg.debug("DiscoverAndSend::pre_inquiry()", __name__)
        self.done = False
        self.thinblue_found_devices=[]

    def find_devices (self, lookup_names=False, 
            duration=8, 
            flush_cache=True):
        
        if self.is_inquiring:
            #raise BluetoothError ("Already inquiring!")
            lg.warning("already_inquiring", __name__)
            return

        self.lookup_names = lookup_names

        self.sock = _gethcisock ()
        if self.sock is None:
            lg.warning("find_devices() sock is None", __name__)
            return
        flt = _bt.hci_filter_new ()
        _bt.hci_filter_all_events (flt)
        _bt.hci_filter_set_ptype (flt, _bt.HCI_EVENT_PKT)

        try:
            self.sock.setsockopt (_bt.SOL_HCI, _bt.HCI_FILTER, flt)
        except Exception, err:
            #raise BluetoothError ("problem with local bluetooth device.")
            lg.warning("Exception: problem with local bluetooth device (setsockopt), error='%s'" %err, __name__)
            return

        # send the inquiry command
        duration = 4
        max_responses = 255
        cmd_pkt = struct.pack ("BBBBB", 0x33, 0x8b, 0x9e, duration, max_responses)

        self.pre_inquiry ()
        
        try:
            _bt.hci_send_cmd (self.sock, _bt.OGF_LINK_CTL, \
                    _bt.OCF_INQUIRY, cmd_pkt)
        except Exception, err:
            #raise BluetoothError ("problem with local bluetooth device.")
            lg.warning("Exception: problem with local bluetooth device (send_cmd), error='%s'" %err, __name__)
            return

        self.is_inquiring = True

        self.names_to_find = {}
        self.names_found = {}

    def device_discovered(self, address, device_class, name):
        lg.debug("device_discovered() %s 0x%X %s" %(address, device_class, name), __name__)
        if address in self.thinblue_found_devices:
            return
        
        # populate bluetooth device type
        major_class = (device_class >> 8) & 0xf
        if major_class < 7:
            blue_type=BLUE_TYPES[major_class]
        else:
            blue_type="unknown"
        
        if blue_type != BLUE_TYPES[2]:
            lg.debug("Device '%s' is not a phone => '%s'" %(address, blue_type), __name__)
            return
        
        phone=Phone(address, device_class, name)
        self.thinblue_found_devices.append(address)
        del(phone)
        lg.debug("device_discovered() finish", __name__)

    def inquiry_complete(self):
        lg.debug("DiscoverAndSend::inquiry_complete()", __name__)
        alladdress=""
        # get all found devices and update database to not set pending a no near phone
        if len(self.thinblue_found_devices):
            for addr in self.thinblue_found_devices:
                alladdress+="'%s',"%addr
            alladdress=alladdress[:-1]
            sql="UPDATE phones SET status='seen1' WHERE address NOT IN (%s) AND status IN ('pending','fail+nopush' )" %( alladdress )
            lg.debug("inquiry_complete() SQL=%s" %sql, __name__)
            thinblue.db.query(sql)
        else:
            sql="UPDATE phones SET status='seen1' WHERE status IN ('pending','fail+nopush' )"
            lg.debug("inquiry_complete() [no bluetooth devices, set all pending||fail+nopush => seen1] SQL=%s" %sql, __name__)
            thinblue.db.query(sql)
        self.done=True


def main():
    lg.debug("init searchs ...", __name__)
    d = DiscoverAndSend()
    lg.debug("first search ", __name__)
    d.find_devices(duration=thinblue.config.timeout)
    readfiles = [ d, ]
    
    while not thinblue.is_stoping():
        try:
            rfds = select.select( readfiles, [], [] )[0]
        except KeyboardInterrupt:
            lg.info("KeyboardInterrupt, exiting...", __name__)
            thinblue.do_stop()
            break

        if d in rfds:
            d.process_event()

        if d.done:
            try:
                time.sleep(2)
            except KeyboardInterrupt:
                lg.info("KeyboardInterrupt, exiting...", __name__)
                thinblue.do_stop()
                break
            
            #lg.info("Re-searching...", __name__)
            d.done=False
            d.find_devices(duration=thinblue.config.timeout)
    lg.info("stopping searchs ...", __name__)





