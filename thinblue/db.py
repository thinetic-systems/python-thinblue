# -*- coding: UTF-8 -*-

import os
import sys
import sqlite
import thinblue.logger as lg
import thinblue.config
import time

conn=None
cursor=None
thinblue.config.lock=False



def create_db():
    lg.debug("Creating empty table phones", __name__)
    sql="""
CREATE TABLE phones (
address VARCHAR(100),
name VARCHAR(255),
blue_type VARCHAR(100),
services TEXT,
status VARCHAR(50),
model VARCHAR(255),
date_search VARCHAR(50),
date_send VARCHAR(50),
PRIMARY KEY (address)
);

CREATE TABLE config (
sendfile TEXT,
debug INTEGER,
timeout INTEGER,
concurrent INTEGER,
stop INTEGER,
file_path TEXT
);

INSERT INTO config (sendfile, debug, timeout, concurrent, stop, file_path) VALUES ('thinetic.jpg', 1, 8, 4, 0, '/var/lib/thinblue/files/');
"""
    f=open("/tmp/db.sql", 'w')
    f.write(sql)
    f.close()
    lg.debug("sqlite %s < /tmp/db.sql" %thinblue.config.DBNAME, __name__)
    os.system("sqlite %s < /tmp/db.sql" %thinblue.config.DBNAME)
    lg.debug("Created '%s' ..."%thinblue.config.DBNAME, __name__)
    os.unlink("/tmp/db.sql")
    import pwd
    for user in pwd.getpwall():
        if "www-data" in user:
            uid=user[2]
            gid=user[3]
            try:
                os.chown(thinblue.config.DBNAME, uid, gid)
            except Exception, err:
                lg.warning("Exception, can't chown database: '%s'"%err, __name__)

            try:
                os.chmod(thinblue.config.DBNAME, 0666)
            except Exception, err:
                lg.warning("Exception, can't chmod 666 database: '%s'"%err, __name__)

def connect():
    global conn
    global cursor
    #lg.debug("Opening database %s"%thinblue.config.DBNAME, __name__)
    if not os.path.isfile(thinblue.config.DBNAME):
        create_db()
    if not os.path.isfile(thinblue.config.DBNAME):
        sys.exit(1)
        
    # database connect or die :(
    try:
        conn = sqlite.connect(db=thinblue.config.DBNAME, autocommit=1)
        cursor = conn.cursor()
    except Exception, err:
        lg.error ( "ThinBlueDB:: ERRROR conecting to database '%s'." %err , __name__)
        return False
    return True

def wait():
    if thinblue.config.lock:
        maxsleep=10
        counter=0
        while thinblue.config.lock and counter < maxsleep:
            time.sleep(0.1)
            lg.debug("waiting for DB lock", __name__)
            counter=counter+1

def query(sql):
    global conn
    global cursor
    
    wait()
    
    result=[]
    # lock database access
    thinblue.config.lock=True
    if not connect():
        lg.error("query() no conection", __name__)
        return result
    
    # do sql query
    if sql[-1] != ";":
        sql="%s;"%sql
    #lg.debug("ThinBlueDB::query ##%s##"%sql, __name__)
    
    try:
        cursor.execute(sql)
    except KeyboardInterrupt:
        lg.error("Keyboard Exception ... wait and retry", __name__)
        wait()
        return query(sql)
    except Exception, err:
        lg.error("Exception while exec SQL: '%s' sql='%s'"%(err,sql), __name__)
        return []
    
    try:
        row = cursor.fetchone()
        if row is not None:
            while row != None:
                result.append(row)
                row = cursor.fetchone()
        # unlock database access
    except Exception, err:
        lg.error("Exception in connect() '%s' SQL='%s'"%(err,sql), __name__)
    close()
    thinblue.config.lock=False
    return result


def close():
    try:
        conn.close()
    except Exception, err:
        lg.warning("Exception closing sqlite connection '%s'"%err, __name__)



