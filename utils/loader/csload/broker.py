"""

   Least-recently used (LRU) queue device
   Clients and workers are shown here in-process

   Author: Guillaume Aubert (gaubert) <guillaume(dot)aubert(at)gmail(dot)com>

"""

import threading
import time
import zmq

NBR_CLIENTS = 2
NBR_WORKERS = 1
import json





def main():

    url_worker = "tcp://0.0.0.0:5558" 

    # Prepare our context and sockets
    context = zmq.Context()
    backend = context.socket(zmq.ROUTER)
    backend.bind(url_worker)



    # Logic of LRU loop
    # - Poll backend always, frontend only if 1+ worker ready
    # - If worker replies, queue worker as ready and forward reply
    # to client if necessary
    # - If client requests, pop next worker and send request to it

    # Queue of available workers
    workers_list      = []

    # init poller
    poller = zmq.Poller()

    # Always poll for worker activity on backend
    poller.register(backend, zmq.POLLIN)

    files=['file1', 'file4', 'file56','file7' ]
    files = range(35)
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

            print "backend message: '%s'" % (message)
            
            
            try:
                j = json.loads(s)
            except ValueError:
                j = json.loads(message[4])
                
            
            if 'Worker' in address and j['status'] in ['READY', 'OK', 'FAILED']:
                print 'appending worker:' ,address
                workers_list.append(address)
        
        if len(workers_list) and len(files):
            f = files.pop()
            worker_id = workers_list.pop()
            j = {'filename': f, 'status':'READY'}
            print 'sent to worker: ', ["something", "", worker_id, "", json.dumps(j)]
            backend.send_multipart([worker_id, "", worker_id, "", json.dumps(j)])
        print workers_list
        
        if len(files) == 0:
            break
    #out of infinite loop: do some housekeeping
    time.sleep (1)

    backend.close()
    context.term()


if __name__ == "__main__":
    main()
