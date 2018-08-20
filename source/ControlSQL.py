"""
Copyright (c) 2015-2016 __Loxoll__. All rights reserved.
"""
import os
import sys
from sqlite3 import *

file_name = os.path.basename(__file__)

class SQL():
    ON = 1
    OFF = 0
    RING_SIZE = 4				# default ring buffer size
    DB_FILE = "LoxollGUI.db"

class xmCT(object):
    """ Circular Table """
    ON = SQL.ON
    OFF = SQL.OFF
    table_size = SQL.RING_SIZE
    
    def __init__(self):
        dbg.printDBG1(file_name, "initiate xmCT - Cirular Table")
        
    def createCT(self, table_name = 'CT', sql_column = ""):
        
        self.table_name = table_name
        
        db_path = './db/'
        db_filename = SQL.DB_FILE
        if not os.path.exists(db_path): os.makedirs(db_path)
        self.conn = connect(db_path + db_filename)

        with self.conn:            
# create Circular Table (CT)
            self.conn.execute("DROP TABLE IF EXISTS %s" % self.table_name)

            query = "CREATE TABLE %s (row_id INTEGER UNSIGNED NOT NULL UNIQUE " % self.table_name + sql_column
            query = query + ", timestamp TIMESTAMP DEFAULT (STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW')) NOT NULL"
            query = query + ", comment VARCHAR(80)"
            query = query + ");"            
            self.conn.execute(query)
            
# initialize Circular Table
            for i in range (0, self.table_size):
                self.__addCT(i, "init "+str(i))
            self.conn.commit()
            
# create Pointer Table
            self.conn.execute("DROP TABLE IF EXISTS ptr%s" % self.table_name)
            query = "CREATE TABLE ptr%s (ptrIn INTEGER UNSIGNED" % self.table_name
            query = query + ", ptrOut INTEGER UNSIGNED"
            query = query + ");"
            self.conn.execute(query)
            query = "insert into ptr%s (ptrIn, ptrOut) values (0, 0)" % self.table_name
            self.conn.execute(query)
            self.conn.commit()
            self.conn.close
            
    def __addCT(self, i, record):
        query = "insert into %s (row_id, comment) values (" % self.table_name + str(i) + ", '" + record + " !')" 
        self.conn.execute(query)
        self.conn.commit()

    def putNextCT(self, engine_idx, dic = {}, comment = ""):

        db_path = './db/'
        db_filename = SQL.DB_FILE
        conn = connect(db_path + db_filename)
        
        table_name = "VPDengine" + str(engine_idx)

# get pointer
        cursor = conn.cursor()
        query = "SELECT * FROM ptr%s" % table_name
        cursor.execute(query)
        ptr_in, ptr_out = cursor.fetchone()
        new_ptr_in = ((ptr_in + 1) % self.table_size)
        if (new_ptr_in == ptr_out):
            if (int(cfg['General']['DEBUG_LEVEL']) >= 2):
                print "-- ring buffer overrun %s offline at %s --" % (table_name, time.time())
        
# update content
        q_head = "UPDATE %s SET comment = \'" % table_name + str(comment) + "'"
        q_tail = " WHERE row_id = " + str(ptr_in)

        q_update = ""
        for key in dic:
            q_update = q_update + ", " + key + "= '" + dic[key] +"'"            
        q_update = q_update + ", timestamp = (STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'))"

        query = q_head + q_update + q_tail
        cursor.execute(query)
        conn.commit()
# update pointer
        query = "UPDATE ptr%s SET ptrIn = " % table_name + str(new_ptr_in)
        cursor.execute(query)
        conn.commit()
        conn.close()

    def getNextCT(self, engine_idx):

        db_path = './db/'
        db_filename = SQL.DB_FILE
        conn = connect(db_path + db_filename)

        table_name = "VPDengine" + str(engine_idx)

        cursor = conn.cursor()
        query = "SELECT * FROM ptr%s" % table_name
        cursor.execute(query)
        ptr_in, ptr_out = cursor.fetchone()

        # update pointer
        query = "UPDATE ptr%s SET ptrOut = " % table_name + str(ptr_in)
        cursor.execute(query)
        conn.commit()

        # get data
        q_head = "select *"
        q_tail = " from %s where row_id = %s" % (table_name, ptr_out)
        query = q_head + q_tail
        cursor.execute(query)
        row = cursor.fetchmany(1)
        conn.close()
        return row
        
    def printCT(self, engine_idx):

        db_path = './db/'
        db_filename = SQL.DB_FILE
        conn = connect(db_path + db_filename)

        table_name = "VPDengine" + str(engine_idx)

        cursor = conn.cursor()
        query = "select * from %s" % table_name
        cursor.execute(query)
        for row in cursor.fetchmany(5):
            print row
        conn.close()
        

if __name__ == '__main__':
    
    print time.time()
    d = xmCT()
    d.createCT(table_name = 'VPDengine0',
             sql_column = ",Uptime,SerialNumber,Firmware,Alert,UniqueID,EngineTime,IPaddress,Revision")
    print time.time()
    
    for i in range (0, (d.table_size + 30)):
        record = "First record for test, make it longer, keep going, up to 80 chars, still not long enough.., "
        record = record + str(i)
        d.putNextCT( 0, comment = record)

    print time.time()
    e = xmCT()
    for row in e.getNextCT( 0):
        row_id,Uptime,SerialNumber,Firmware,Alert,UniqueID,EngineTime,IPaddress,Revision,timestamp,comment = row
    print time.time()
    
    print row_id,Uptime,SerialNumber,UniqueID,EngineTime,IPaddress,Revision,timestamp
    print "Alert =", Alert
    print "Firmware = ", Firmware
    
    d.printCT( 0)
    
    sys.exit()
