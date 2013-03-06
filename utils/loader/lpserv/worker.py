"""

   Least-recently used (LRU) queue device
   Demonstrates use of pyzmq IOLoop reactor

   While this example runs in a single process, that is just to make
   it easier to start and stop the example. Each thread has its own
   context and conceptually acts as a separate process.

   Author: Min RK <benjaminrk(at)gmail(dot)com>
   Adapted from lruqueue.py by Guillaume Aubert (gaubert) <guillaume(dot)aubert(at)gmail(dot)com>

"""

import threading
import time
import zmq
import json


NBR_WORKERS = 4

def worker_thread(worker_url, i):
    """ Worker using REQ socket to do LRU routing """
    
    context = zmq.Context()
    socket = context.socket(zmq.REQ)

    identity = "Worker-%d" % (i)

    socket.setsockopt(zmq.IDENTITY, identity) #set worker identity

    socket.connect(worker_url)

    # Tell the borker we are ready for work
    
    j = {'status':'READY', 'address':identity }
    socket.send(json.dumps(j))

    try:
        while True:
            
            message = socket.recv_multipart()
            print 'message: ', message
            address, empty, s = message[0], message[1], message[2]
            # import pdb;pdb.set_trace()
            j = json.loads(s)
            assert empty == ""
            print("%s: %s\n" %(identity, j))
            
            j['status'] = 'OK'
            # j['address'] = identity
            print 'did work, sending: ', [address, "", json.dumps(j)]
            socket.send_multipart([address, "", json.dumps(j)])

    except zmq.ZMQError, zerr:
        # context terminated so quit silently
        if zerr.strerror == 'Context was terminated':
            return
        else:
            raise zerr




def main():
    """main method"""

    url_worker = "tcp://0.0.0.0:5558"

    for i in range(NBR_WORKERS):
        thread = threading.Thread(target=worker_thread, args=(url_worker, i, ))
        thread.start()




if __name__ == "__main__":
    main()