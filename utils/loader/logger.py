# Task sink
# Binds PULL socket to tcp://localhost:5558
# Collects results from workers via that socket
#
# Author: Lev Givon <lev(at)columbia(dot)edu>

import sys
import time
import zmq
import psycopg2
import json

def create_log_table(connection, tablename):

    cur = connection.cursor()
    cur.execute("select tablename from pg_tables where tablename ilike '%s'" % tablename)
    exists = cur.fetchone()
    if not exists:
        cur.execute('CREATE TABLE %s(FILENAME text, SUCCESS bool, ERROR text)'% tablename)
        connection.commit()

def log_data(connection, tablename, j):
    cur = connection.cursor()

    insert = "INSERT INTO %s (FILENAME, SUCCESS, ERROR) values ('%s', '%s', '%s')" % (table_name, j['filename'], j['success'], j['error'])
    cur.execute(insert)
    connection.commit()
    
if __name__=='__main__':
    table_name = 'log'
    connection = psycopg2.connect('host=localhost user=plasio dbname=iowa')
    create_log_table(connection, table_name)

    context = zmq.Context()

    # Socket to receive messages on
    receiver = context.socket(zmq.PULL)
    receiver.bind("tcp://*:5558")


    while True:
        s = receiver.recv()
        
        j = json.loads(s)
        
        if 'status' in j.keys():
            print j
            if j['status'] == 'end':
                break
            continue
        log_data(connection, table_name,  j)

