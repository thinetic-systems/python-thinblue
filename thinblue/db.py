# -*- coding: UTF-8 -*-

import os
import sys
import thinblue.logger as lg
import thinblue.config
import time

from pysqlite2 import dbapi2 as sqlite3
sqlite3.enable_callback_tracebacks(True)

import threading
mutex = threading.Lock()


class Sqlite3():
    def __init__(self, db):
        #lg.debug("MultiThreadOK():: init dbname=%s"%db, __name__)
        self.db=db
    def run(self, sql, exe=False):
        con = sqlite3.connect(self.db)
        con.isolation_level = None
        cursor = con.cursor()
        cursor.execute(sql)
        result=[]
        if not exe:
            for row in cursor: result.append(row)
        
        # lock
        mutex.acquire()
        con.commit()
        # unlock
        mutex.release()
        
        cursor.close()
        con.close()
        return result
    
    def select(self, sql):
        return self.run(sql)
    
    def execute(self, sql):
        self.run(sql, exe=True)

    def close(self, *args):
        lg.debug("    close called", __name__)




__sql__=Sqlite3(thinblue.config.DBNAME)

def create_db():
    lg.debug("Creating empty table phones", __name__)
    __sql__.execute("""CREATE TABLE phones (address VARCHAR(100), 
                                            name VARCHAR(255), 
                                            blue_type VARCHAR(100), 
                                            services TEXT,  
                                            status VARCHAR(50), 
                                            model VARCHAR(255), 
                                            date_search VARCHAR(50), 
                                            date_send VARCHAR(50), 
                                            PRIMARY KEY (address) )""")
    
    __sql__.execute("""CREATE TABLE config (sendfile TEXT, 
                                            debug INTEGER, 
                                            timeout INTEGER, 
                                            concurrent INTEGER, 
                                            stop INTEGER, 
                                            file_path TEXT )""")
    
    __sql__.execute("""INSERT INTO config (sendfile, 
                                           debug, 
                                           timeout, 
                                           concurrent, 
                                           stop, 
                                           file_path) 
                                    VALUES ('thinetic.jpg', 
                                             1, 
                                             8, 
                                             4, 
                                             0, 
                                             '/var/lib/thinblue/files/')""")
    return

def connect():
    raise "connect() called and not needed"

def query(_sql):
    #lg.debug("query() sql=%s" %_sql, __name__)
    if "SELECT" in _sql or "select" in _sql:
        _res=__sql__.select(_sql)
    else:
        _res=__sql__.execute(_sql)
    result=[]
    if _res:
        for f in _res:
            result.append(f)
    lg.debug("query() sql='%s' result='%s'" %(_sql, result) , __name__)
    return result

def close():
    global __sql__
    lg.debug("close()", __name__)
    __sql__.close()



if __name__=='__main__':
    #thinblue.config.debug=True
    #lg.info("running", __name__)
    db='people.db'
    sql=Sqlite3(db)
    sql.execute("create table people2(name,first)")
    sql.execute("insert into people2 values('VAN ROSSUM','Guido')")
    sql.execute("insert into people2 values('TORVALDS','Linus')")
    for row in sql.select("select first, name from people2"):
        print row
    print "db.py: exiting..."






