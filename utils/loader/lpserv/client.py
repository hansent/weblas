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

from zmq.eventloop.ioloop import IOLoop
from zmq.eventloop.zmqstream import ZMQStream

NBR_CLIENTS = 2


def client_thread(client_url, i):
    """ Basic request-reply client using REQ socket """
    
    context = zmq.Context()
    
    socket = context.socket(zmq.REQ)

    identity = "Client-%d" % (i)

    socket.setsockopt(zmq.IDENTITY, identity) #Set client identity. Makes tracing easier

    socket.connect(client_url)

    #  Send request, get reply
    j = {'status':'HELLO', 'address':identity }
    message = [identity, "", json.dumps(j)]
    message = json.dumps(j)
    print 'client sending: ', message
    # socket.send_multipart(message)
    socket.send(message) 
    
    try:
        while True:
            message =  socket.recv_multipart()
            print 'received from backend.recv_multipart(): ', message
            
            j = json.loads(message[0])
            if j['status'] == 'FAILED':
                print 'request failed for %s' % identity
            time.sleep (0.01)
            print("%s: %s\n" % (identity, message))

            return

    except zmq.ZMQError, zerr:
        # context terminated so quit silently
        if zerr.strerror == 'Context was terminated':
            return
        else:
            raise zerr





def main():
    """main method"""
    
    import sys
    
    url_client = "tcp://0.0.0.0:5557" 

    if len(sys.argv) > 1:
        NBR_CLIENTS = int(sys.argv[1])
        
    for i in range(NBR_CLIENTS):
        thread_c = threading.Thread(target=client_thread, args=(url_client, i, ))
        thread_c.start()




if __name__ == "__main__":
    main()