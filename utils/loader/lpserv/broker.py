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
            message = backend.recv_multipart()

            assert available_workers < NBR_WORKERS

            worker_addr = message[0]

            # add worker back to the list of workers
            available_workers += 1
            workers_list.append(worker_addr)

            #   Second frame is empty
            empty        = message[1]
            assert empty == ""

            # Third frame is READY or else a client reply address
            client_addr = message[2]

            # If client reply, send rest back to frontend
            if client_addr != "READY":

                # Following frame is empty
                empty = message[3]
                assert empty == ""

                reply = message[4]

                frontend.send_multipart([client_addr, "", reply])

                client_nbr -= 1

                # if client_nbr == 0:
      #               break  # Exit after N messages

        # poll on frontend only if workers are available
        if available_workers > 0:

            if (frontend in socks and socks[frontend] == zmq.POLLIN):
                # Now get next client request, route to LRU worker
                # Client request is [address][empty][request]

                [client_addr, empty, request ] = frontend.recv_multipart()

                assert empty == ""

                #  Dequeue and drop the next worker address
                available_workers -= 1
                worker_id = workers_list.pop()

                backend.send_multipart([worker_id, "", client_addr, "", request])


    #out of infinite loop: do some housekeeping
    time.sleep (1)

    frontend.close()
    backend.close()
    context.term()


if __name__ == "__main__":
    main()
