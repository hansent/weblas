"""

   Least-recently used (LRU) queue device
   Clients and workers are shown here in-process

   Author: Guillaume Aubert (gaubert) <guillaume(dot)aubert(at)gmail(dot)com>

"""

import threading
import time
import zmq
import subprocess
import json
import os

def get_files(directory):
    l = 'ls %s' % directory
    process = subprocess.Popen(l.split(), shell=False, stdout=subprocess.PIPE)
    files = process.communicate()[0].split()
    return files
    



def main():

    url_worker = "tcp://0.0.0.0:5558" 
    url_worker = 'ipc://worker'  
    logger_url = 'ipc://logger'  
    # Prepare our context and sockets
    context = zmq.Context()
    backend = context.socket(zmq.ROUTER)
    backend.bind(url_worker)

    workers_list      = []

    # init poller
    poller = zmq.Poller()

    # Always poll for worker activity on backend
    poller.register(backend, zmq.POLLIN)

    DATADIR='/Volumes/lidar4/raw'
    files = get_files(DATADIR)
    # files=files[0:10]
    while True:

        socks = dict(poller.poll())
        # Handle worker activity on backend
        if (backend in socks and socks[backend] == zmq.POLLIN):

            # Queue worker address for LRU routing
            # print 'backend.recv_multipart(): ', backend.recv_multipart()
            message =  backend.recv_multipart()
            print 'received from backend.recv_multipart(): ', message
            address, empty, s = message[0], message[1], message[2]

            #   Second frame is empty
            assert empty == ""

            # print "backend message: '%s'" % (message)
            
            
            try:
                j = json.loads(s)
            except ValueError:
                j = json.loads(message[4])
                
            
            if 'Worker' in address and j['status'] in ['READY', 'OK', 'FAILED']:
                # print 'appending worker:' ,address
                workers_list.append(address)
        
        if len(workers_list) and len(files):
            f = files.pop()
            worker_id = workers_list.pop()
            lazfile = os.path.join(DATADIR, f)
            j = {'filename': lazfile, 'status':'READY', 'task':'LOAD'}
            backend.send_multipart([worker_id, "", worker_id, "", json.dumps(j)])
        
        if len(files) == 0:
            break

    time.sleep (1)

    backend.close()
    context.term()


if __name__ == "__main__":
    main()
