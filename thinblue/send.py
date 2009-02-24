# -*- coding: UTF-8 -*-

import socket
socket.setdefaulttimeout(30)


import thinblue.logger as lg
import thinblue.config
import thinblue.db
import lightblue.obex

import time
import os

#############################################################################
import types
import datetime

import lightblue
from lightblue import _lightbluecommon
from lightblue import _obexcommon
import _lightblueobex    # python extension

from lightblue._obexcommon import OBEXError




class OBEXClient(lightblue.obex._obex.OBEXClient):
    def __init__(self, address, channel):
        if not isinstance(address, types.StringTypes):
            raise TypeError("address must be string, was %s" % type(address))
        if not type(channel) == int:
            raise TypeError("channel must be int, was %s" % type(channel))

        self.__sock = None
        self.__client = None
        self.__serveraddr = (address, channel)
        self.__connectionid = None
        self.__connected=False
        lg.debug("OBEXClient() __init__()", __name__)

    def __setUp(self):
        lg.debug("OBEXClient() __setup()", __name__)
        if self.__client is None:
            import bluetooth
            self.__sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            try:
                self.__sock.connect((self.__serveraddr[0],
                                     self.__serveraddr[1]))
            except bluetooth.BluetoothError, e:
                #raise OBEXError(str(e))
                lg.debug("Exception OBEXClient() (BluetoothError) __setUp, error='%s'" %e, __name__)
                self.__connected=False
                return
            try:
                self.__client = _lightblueobex.OBEXClient(self.__sock.fileno())
            except IOError, e:
                #raise OBEXError(str(e))
                lg.debug("Exception OBEXClient() __setUp, error='%s'" %e, __name__)
                self.__connected=False
            self.__connected=True

    def connect(self, headers={}):
        lg.debug("OBEXClient() connect", __name__)
        if self.__client is not None:
            #raise OBEXError("session is already connected")
            lg.debug("OBEXClient() connect, (client != None) ", __name__)
            return False
        
        self.__setUp()
        if not self.__connected:
            lg.warning("OBEXClient() connect NOT CONNECTED", __name__)
            return False

        try:
            resp = self.__client.request(_lightblueobex.CONNECT,
                    self.__convertheaders(headers), None)
        except IOError, e:
            #raise OBEXError(str(e))
            lg.debug("Exception OBEXClient() connect, error='%s'" %e, __name__)
            return False

        result = self.__createresponse(resp)
        if result.code == _obexcommon.OK:
            self.__connectionid = result.headers.get("connection-id", None)
        else:
            self.__closetransport()
        lg.debug("OBEXClient() connect result='%s'"%result, __name__)
        return result

    def put(self, headers, fileobj):
        lg.debug("OBEXClient() put", __name__)
        if not hasattr(fileobj, "read"):
            raise TypeError("file-like object must have read() method")
        self.__checkconnected()

        try:
            resp = self.__client.request(_lightblueobex.PUT,
                    self.__convertheaders(headers), None, fileobj)
        except IOError, e:
            #raise OBEXError(str(e))
            lg.debug("Exception OBEXClient() put, error='%s'"%e, __name__)
        return self.__createresponse(resp)

    def __closetransport(self):
        lg.debug("OBEXClient() __closetransport", __name__)
        try:
            self.__sock.close()
        except:
            pass
        self.__connectionid = None
        self.__client = None

def sendfile(address, channel, source):
    if not _lightbluecommon._isbtaddr(address):
        raise TypeError("address '%s' is not a valid bluetooth address" \
            % address)
    if not isinstance(channel, int):
        raise TypeError("channel must be int, was %s" % type(channel))
    if not isinstance(source, types.StringTypes) and \
            not hasattr(source, "read"):
        raise TypeError("source must be string or file-like object with read() method")

    if isinstance(source, types.StringTypes):
        headers = {"name": os.path.basename(source)}
        fileobj = file(source, "rb")
        closefileobj = True
    else:
        if hasattr(source, "name"):
            headers = {"name": source.name}
        fileobj = source
        closefileobj = False

    client = OBEXClient(address, channel)
    if not client.connect():
        return

    try:
        resp = client.put(headers, fileobj)
    finally:
        if closefileobj:
            fileobj.close()
        try:
            client.disconnect()
        except:
            pass    # always ignore disconnection errors

    if resp.code != _obexcommon.OK:
        #raise OBEXError("server denied the Put request")
        lg.warning("sendfile() put error='%s'"%resp, __name__)
        return False
    return True
    



#############################################################################

def main():
    lg.debug("init sending ...", __name__)
    time.sleep(5)
    while not thinblue.is_stoping():
        # FIXME How much time?
        _file=os.path.join( thinblue.config.file_path , thinblue.config.sendfile )
        
        if thinblue.config.sendfile == "":
            lg.error(" **** No file configured, skipping send... ****", __name__)
            continue
        
        if  not os.path.isfile(_file):
            lg.error(" **** file (%s) not found, skipping send... ****"%_file, __name__)
            continue

        sql="SELECT address,status from phones WHERE status='pending';"
        pending=thinblue.db.query(sql)
        lg.info("Pending send devices=%s"%pending, __name__)

        if len(pending) == 0:
            time.sleep(5)
            continue
        
        for phone in pending:
            try:
                result=sendfile(phone[0], 4, _file)
            except KeyboardInterrupt:
                lg.info("KeyboardInterrupt, exiting...", __name__)
                thinblue.do_stop()
                break
        
            if result:
                # update status if sendfile is OK
                sql="UPDATE phones set status='send' WHERE address='%s';"%phone[0]
                lg.info("Setting status='send' in device=%s"%phone[0], __name__)
                thinblue.db.query(sql)
            else:
                # update status if sendfile is KO
                sql="UPDATE phones set status='fail' WHERE address='%s';"%phone[0]
                lg.warning("Setting status='fail' in device=%s"%phone[0], __name__)
                thinblue.db.query(sql)
    lg.info("stopping sending ...", __name__)


