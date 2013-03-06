"""

   Least-recently used (LRU) queue device
   Clients and workers are shown here in-process

   Author: Guillaume Aubert (gaubert) <guillaume(dot)aubert(at)gmail(dot)com>

"""

import threading
import time
import zmq

NBR_CLIENTS = 4
NBR_WORKERS = 3
import json





def main():

    url_worker = "tcp://0.0.0.0:5557" 
    url_client = "tcp://0.0.0.0:5558" 
    
    client_nbr = NBR_CLIENTS

    # Prepare our context and sockets
    context = zmq.Context()
    frontend = context.socket(zmq.ROUTER)
    frontend.bind(url_client)
    backend = context.socket(zmq.ROUTER)
    backend.bind(url_worker)



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

        # Handle worker activity on backend
        if (backend in socks and socks[backend] == zmq.POLLIN):

            # Queue worker address for LRU routing
            print 'backend.recv_multipart(): ', backend.recv_multipart()
            address, empty, s = backend.recv_multipart()
            print "backend message: '%s'" % ([address, empty, s])

            assert available_workers < NBR_WORKERS

            worker_addr = address

            # add worker back to the list of workers
            available_workers += 1
            workers_list.append(worker_addr)

            #   Second frame is empty
            assert empty == ""

            # Third frame is READY or else a client reply address
            j = json.loads(s)
            client_addr = j['address']
            
            print 'client_addr: ', client_addr

            # If client reply, send rest back to frontend
            if j['status'] != "READY":

                # Following frame is empty

                reply = j['status']
                j = {'status':j['status'], 'address':client_addr }

                frontend.send_multipart([str(client_addr), "", json.dumps(j)])

                client_nbr -= 1

                # if client_nbr == 0:
      #               break  # Exit after N messages

        # poll on frontend only if workers are available
        if available_workers > 0:

            if (frontend in socks and socks[frontend] == zmq.POLLIN):
                # Now get next client request, route to LRU worker
                # Client request is [address][empty][request]

                address, empty, s = frontend.recv_multipart()

                assert empty == ""

                #  Dequeue and drop the next worker address
                available_workers -= 1
                worker_id = workers_list.pop()
                
                print 's: ', s
                j = json.loads(s)
                print 'json: ', j
                s = json.dumps(j)
                backend.send_multipart([worker_id, "", address, "", s])


    #out of infinite loop: do some housekeeping
    time.sleep (1)

    frontend.close()
    backend.close()
    context.term()


if __name__ == "__main__":
    main()
