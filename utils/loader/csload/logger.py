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
import copy

def create_log_table(connection, tablename):

    cur = connection.cursor()
    cur.execute("select tablename from pg_tables where tablename ilike '%s'" % tablename)
    exists = cur.fetchone()
    if not exists:
        cur.execute('CREATE TABLE %s(FILENAME text, SUCCESS bool, ERROR text)'% tablename)
        connection.commit()

def log_data(connection, tablename, j):
    cur = connection.cursor()

    data = copy.copy(j)
    data['error'] = repr(data['error'])
    insert = 'INSERT INTO %s (FILENAME, SUCCESS, ERROR) values ' % tablename
    query = insert + "(%(filename)s, %(success)s, %(error)s)" 

    cur.execute(query, data)
    connection.commit()

    
if __name__=='__main__':
    table_name = 'log'
    connection = psycopg2.connect('host=localhost user=plasio dbname=iowa')
    create_log_table(connection, table_name)

    context = zmq.Context()

    logger_port = 5559
    workers = 1
    if len(sys.argv) > 1:
        logger_port = sys.argv[1]
        
    logger_url = "tcp://0.0.0.0:%d" % logger_port

    # Socket to receive messages on
    receiver = context.socket(zmq.PULL)
    receiver.bind(logger_url)


    while True:
        message =  receiver.recv_multipart()
        # print 'received from backend.recv_multipart(): ', message
        address, empty, s = message[0], message[1], message[2]

        
        j = json.loads(s)
        
        if j['status'] == 'END':
            break

        log_data(connection, table_name,  j)
        continue
