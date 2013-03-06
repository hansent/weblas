"""

   Least-recently used (LRU) queue device
   Clients and workers are shown here in-process

   Author: Guillaume Aubert (gaubert) <guillaume(dot)aubert(at)gmail(dot)com>

"""

import threading
import time
import zmq

NBR_CLIENTS = 20
NBR_WORKERS = 4
import json





def main():

    url_worker = "tcp://0.0.0.0:5558" 
    url_client = "tcp://0.0.0.0:5557" 
    
    client_nbr = NBR_CLIENTS

    # Prepare our context and sockets
    context = zmq.Context()
    frontend = context.socket(zmq.ROUTER)
    frontend.bind(url_client)
    backend = context.socket(zmq.ROUTER)
    backend.bind(url_worker)

    # frontend.setsockopt(zmq.IDENTITY, 'Broker-Cleint')
    # backend.setsockopt(zmq.IDENTITY, 'Broker-Werker')

    # create workers and clients threads



    # Logic of LRU loop
    # - Poll backend always, frontend only if 1+ worker ready
    # - If worker replies, queue worker as ready and forward reply
    # to client if necessary
    # - If client requests, pop next worker and send request to it

    # Queue of available workers
    available_workers = 0
    workers_list      = []

    # init poller
    poller = zmq.Poller()

    # Always poll for worker activity on backend
    poller.register(backend, zmq.POLLIN)

    # Poll front-end only if we have available workers
    poller.register(frontend, zmq.POLLIN)

    while True:

        socks = dict(poller.poll())
        # import pdb;pdb.set_trace()

        # Handle worker activity on backend
        if (backend in socks and socks[backend] == zmq.POLLIN):

            # Queue worker address for LRU routing
            # print 'backend.recv_multipart(): ', backend.recv_multipart()
            message =  backend.recv_multipart()
            print 'received from backend.recv_multipart(): ', message
            address, empty, s = message[0], message[1], message[2]

            #   Second frame is empty
            assert empty == ""

            print "backend message: '%s'" % ([message])
            
            try:
                j = json.loads(s)
            except ValueError:
                j = json.loads(message[4])
                frontend.send_multipart([s, "", json.dumps(j)])
                
            assert available_workers < NBR_WORKERS

            # add worker back to the list of workers
            available_workers += 1
            
            if 'Worker' in address and j['status'] in ['READY', 'OK']:
                workers_list.append(address)
            elif 'Client' in j['address'] and j['status'] == 'HELLO':

                reply = j['status']
                j = {'status':j['status'], 'address':client_addr }
                
                print 'sending to frontend: ', [str(j['address']), "", json.dumps(j)]
                frontend.send_multipart([str(j['address']), "", json.dumps(j)])
                
                client_nbr -= 1

            assert len(workers_list) == available_workers
            
        # import pdb;pdb.set_trace()
        # poll on frontend only if workers are available
        if available_workers > 0:
            # import pdb;pdb.set_trace()
            if (frontend in socks and socks[frontend] == zmq.POLLIN):
                # Now get next client request, route to LRU worker
                # Client request is [address][empty][request]
                
                message = frontend.recv_multipart()
                print 'frontend message recv_multipart: ', message
                address, empty, s = message
                print "frontend message: '%s'" % ([address, empty, s])
                assert empty == ""

                #  Dequeue and drop the next worker address
                available_workers -= 1
                worker_id = workers_list.pop()
                
                j = json.loads(s)

                j['something'] = 'something'
                s = json.dumps(j)
                
                # import pdb;pdb.set_trace()
                print 'sending to backend: ',[worker_id, "", str(j['address']), "", json.dumps(j)]
                # backend.send_multipart([worker_id, "", s])
                backend.send_multipart([worker_id, "", str(j['address']), "", json.dumps(j)])

    #out of infinite loop: do some housekeeping
    time.sleep (1)

    frontend.close()
    backend.close()
    context.term()


if __name__ == "__main__":
    main()
